# backend/solver.py
from __future__ import annotations
import time
import random
from itertools import combinations
from typing import List, Tuple, Dict

from ofcp_core import Card, parse_card, card_code, full_deck, valid_order, table_scores_4p
from ofcp_core import evaluate_hand, royalties
from bots_fullhand import arrange_greedy

Piles = Tuple[List[Card], List[Card], List[Card]]  # (top3, mid5, bot5)

def piles_to_codes(p: Piles) -> Dict[str, List[str]]:
    top, mid, bot = p
    return {
        "top": [card_code(c) for c in top],
        "middle": [card_code(c) for c in mid],
        "bottom": [card_code(c) for c in bot],
    }

def quick_rank_score(p: Piles) -> float:
    """
    Cheap heuristic to shortlist candidate layouts:
      - big bonus if valid order
      - royalties
      - bottom+middle strength
      - mild penalty if top too strong
    """
    top, mid, bot = p
    t = evaluate_hand(top)
    m = evaluate_hand(mid)
    b = evaluate_hand(bot)

    sc = 0.0
    sc += 50.0 if valid_order(top, mid, bot) else -200.0
    sc += 3.0 * royalties(top, mid, bot)
    sc += 4.0 * b[0] + 2.0 * m[0] - 1.0 * t[0]
    # tiebreak
    def v(x):
        return max(x[1]) if isinstance(x[1], list) else x[1]
    sc += 0.05 * (v(b) + 0.7 * v(m) + 0.3 * v(t))
    return sc

def all_splits_13(cards: List[Card]):
    """
    Enumerate all (top3, mid5, bot5) splits.
    Count = C(13,3)*C(10,5)=72072
    """
    idxs = list(range(13))
    for top_idx in combinations(idxs, 3):
        rem1 = [i for i in idxs if i not in top_idx]
        top = [cards[i] for i in top_idx]
        for mid_idx_rel in combinations(rem1, 5):
            rem2 = [i for i in rem1 if i not in mid_idx_rel]
            mid = [cards[i] for i in mid_idx_rel]
            bot = [cards[i] for i in rem2]
            yield (top, mid, bot)

def monte_carlo_winrate(
    my_piles: Piles,
    remaining_deck: List[Card],
    sims: int,
    rng: random.Random
) -> Tuple[float, float]:
    """
    Simulate 4P table vs 3 opponents:
      - sample 39 cards for opponents (13 each) from remaining deck
      - each opponent arranged by heuristic arrange_greedy
      - score table using pairwise heads-up totals
    Return:
      winrate (unique table win fraction),
      avg_margin (my_score - avg(other_scores))
    """
    wins = 0
    margin_sum = 0.0

    for _ in range(sims):
        draw = rng.sample(remaining_deck, 39)
        opp1 = draw[0:13]
        opp2 = draw[13:26]
        opp3 = draw[26:39]

        p1 = arrange_greedy(opp1)
        p2 = arrange_greedy(opp2)
        p3 = arrange_greedy(opp3)

        piles4 = [my_piles, p1, p2, p3]
        scores = table_scores_4p(piles4)

        my = scores[0]
        best = max(scores)
        if my == best and scores.count(best) == 1:
            wins += 1

        others = [scores[i] for i in range(1, 4)]
        margin_sum += my - (sum(others) / 3.0)

    return wins / sims, margin_sum / sims

def solve_best_arrangement(
    cards13_codes: List[str],
    time_limit_sec: float = 55.0,   # keep < 180 (3 minutes)
    shortlist_k: int = 250,
    mc_min_sims: int = 200,
    mc_max_sims: int = 5000,
    seed: int = 1
):
    start = time.monotonic()
    rng = random.Random(seed)

    if len(cards13_codes) != 13:
        raise ValueError("Need exactly 13 cards.")
    cards13 = [parse_card(c) for c in cards13_codes]
    if len({(c.rank, c.suit) for c in cards13}) != 13:
        raise ValueError("Duplicate cards in input.")

    deck = full_deck()
    used = {(c.rank, c.suit) for c in cards13}
    remaining = [c for c in deck if (c.rank, c.suit) not in used]

    # 1) enumerate all splits, compute quick score, keep top-K
    scored = []
    for p in all_splits_13(cards13):
        scored.append((quick_rank_score(p), p))
    scored.sort(key=lambda x: x[0], reverse=True)
    candidates = [p for _, p in scored[:shortlist_k]]

    # 2) Monte Carlo on candidates until time runs out
    best = None
    best_wr = -1.0
    best_margin = -1e18

    # adaptive sims per candidate
    # (start small; allocate more to top contenders while time remains)
    sims_per = mc_min_sims

    for i, p in enumerate(candidates):
        # time check
        if time.monotonic() - start > time_limit_sec:
            break

        # allocate sims (increase as we get closer to best)
        # More sims for top 50, fewer for tail.
        if i < 25:
            sims_per = min(mc_max_sims, max(mc_min_sims, int(mc_min_sims * 6)))
        elif i < 100:
            sims_per = min(mc_max_sims, max(mc_min_sims, int(mc_min_sims * 3)))
        else:
            sims_per = mc_min_sims

        wr, margin = monte_carlo_winrate(p, remaining, sims_per, rng)

        # choose by winrate first, then margin
        if (wr > best_wr) or (wr == best_wr and margin > best_margin):
            best_wr = wr
            best_margin = margin
            best = p

    if best is None:
        # fallback: best quick score
        best = candidates[0]
        best_wr = 0.0
        best_margin = 0.0

    elapsed = time.monotonic() - start
    return {
        "best": piles_to_codes(best),
        "estimated_winrate": best_wr,
        "estimated_margin": best_margin,
        "elapsed_sec": elapsed,
        "shortlist_k": len(candidates),
    }