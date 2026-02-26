# backend/ofcp_core.py
import random
from collections import namedtuple, Counter

Card = namedtuple("Card", ["rank", "suit"])

RANKS = "23456789TJQKA"
SUITS = "CDHS"

def parse_card(code: str) -> Card:
    code = code.strip().upper()
    if len(code) != 2:
        raise ValueError(f"Bad card code: {code}")
    r, s = code[0], code[1]
    if r not in RANKS or s not in SUITS:
        raise ValueError(f"Bad card code: {code}")
    return Card(r, s)

def card_code(c: Card) -> str:
    return f"{c.rank}{c.suit}"

def full_deck():
    return [Card(r, s) for r in RANKS for s in SUITS]

def evaluate_hand(cards):
    """
    Returns comparable tuple (category, tiebreaker)
    category higher is better.
    NOTE: This is the same style as your previous project implementation.
    """
    rank_values = {r: i for i, r in enumerate(RANKS, 2)}
    counts = Counter(card.rank for card in cards)
    suits = [card.suit for card in cards]
    rank_counts = sorted(counts.values(), reverse=True)

    if len(cards) == 1:
        return (0, sorted([rank_values[c.rank] for c in cards], reverse=True))

    if len(cards) == 2:
        if rank_counts == [2]:
            return (1, rank_values[max(counts, key=lambda k: (counts[k], rank_values[k]))])
        return (0, sorted([rank_values[c.rank] for c in cards], reverse=True))

    if len(cards) == 3:
        if rank_counts == [3]:
            return (3, rank_values[max(counts, key=counts.get)])
        if rank_counts == [2, 1]:
            return (1, rank_values[max(counts, key=lambda k: (counts[k], rank_values[k]))])
        return (0, sorted([rank_values[c.rank] for c in cards], reverse=True))

    if len(cards) == 4:
        if rank_counts == [3, 1]:
            return (3, rank_values[max(counts, key=counts.get)])
        if rank_counts == [2, 2]:
            pairs = sorted([rank_values[r] for r, c in counts.items() if c == 2], reverse=True)
            return (2, pairs)
        if rank_counts == [2, 1, 1]:
            return (1, rank_values[max(counts, key=counts.get)])
        return (0, sorted([rank_values[c.rank] for c in cards], reverse=True))

    # 5 cards
    is_flush = (len(set(suits)) == 1)
    sorted_ranks = sorted([rank_values[c.rank] for c in cards])
    is_straight = (sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)))

    if is_straight and is_flush:
        return (8, sorted_ranks[-1])
    if rank_counts == [4, 1]:
        return (7, rank_values[max(counts, key=counts.get)])
    if rank_counts == [3, 2]:
        return (6, rank_values[max(counts, key=counts.get)])
    if is_flush:
        return (5, sorted_ranks[::-1])
    if is_straight:
        return (4, sorted_ranks[-1])
    if rank_counts == [3, 1, 1]:
        return (3, rank_values[max(counts, key=counts.get)])
    if rank_counts == [2, 2, 1]:
        pairs = sorted([rank_values[r] for r, c in counts.items() if c == 2], reverse=True)
        return (2, pairs)
    if rank_counts == [2, 1, 1, 1]:
        return (1, rank_values[max(counts, key=counts.get)])
    return (0, sorted_ranks[::-1])

def compare_hands(h1, h2):
    return 1 if h1 > h2 else (2 if h1 < h2 else 0)

def calculate_royalties_top(hand3):
    # minimal royalties table (same as your code)
    rank_values = {r: i for i, r in enumerate(RANKS, 2)}
    top_royalties = {
        "66": 1, "77": 2, "88": 3, "99": 4, "TT": 5, "JJ": 6, "QQ": 7, "KK": 8, "AA": 9,
        "222": 10, "333": 11, "444": 12, "555": 13, "666": 14, "777": 15, "888": 16,
        "999": 17, "TTT": 18, "JJJ": 19, "QQQ": 20, "KKK": 21, "AAA": 22
    }
    ranks = "".join(sorted([c.rank for c in hand3], key=lambda x: rank_values[x]))
    return top_royalties.get(ranks, 0)

def calculate_royalties_5(hand5, position):
    middle_bottom_royalties = {
        "middle": {"Three of a kind": 2, "Straight": 4, "Flush": 8, "Full house": 12,
                   "Four of a kind": 20, "Straight flush": 30, "Royal flush": 50},
        "bottom": {"Three of a kind": 0, "Straight": 2, "Flush": 4, "Full house": 6,
                   "Four of a kind": 10, "Straight flush": 15, "Royal flush": 25}
    }
    strength = evaluate_hand(hand5)
    hands_map = {
        8: "Straight flush",
        7: "Four of a kind",
        6: "Full house",
        5: "Flush",
        4: "Straight",
        3: "Three of a kind",
    }
    return middle_bottom_royalties[position].get(hands_map.get(strength[0]), 0)

def royalties(top3, mid5, bot5):
    r = 0
    r += calculate_royalties_top(top3)
    r += calculate_royalties_5(mid5, "middle")
    r += calculate_royalties_5(bot5, "bottom")
    return r

def valid_order(top3, mid5, bot5) -> bool:
    t = evaluate_hand(top3)
    m = evaluate_hand(mid5)
    b = evaluate_hand(bot5)
    return b >= m >= t

def score_heads_up(pA, pB):
    """
    pA/pB = (top3, mid5, bot5)
    returns points (A,B) with foul/royalty/rows/scoop rules
    """
    A_top, A_mid, A_bot = pA
    B_top, B_mid, B_bot = pB

    A_foul = not valid_order(A_top, A_mid, A_bot)
    B_foul = not valid_order(B_top, B_mid, B_bot)

    A_pts = 0
    B_pts = 0

    # foul base
    if (not A_foul) and (not B_foul):
        A_pts += 6
        B_pts += 6
    elif (not A_foul) and B_foul:
        A_pts += 6
        B_pts -= 6
    elif A_foul and (not B_foul):
        A_pts -= 6
        B_pts += 6

    # royalties
    if not A_foul:
        A_pts += royalties(A_top, A_mid, A_bot)
    if not B_foul:
        B_pts += royalties(B_top, B_mid, B_bot)

    # compare rows
    A_rows = 0
    B_rows = 0
    if not A_foul:
        A_vals = (evaluate_hand(A_bot), evaluate_hand(A_mid), evaluate_hand(A_top))
    else:
        A_vals = ((0, [0]),) * 3
    if not B_foul:
        B_vals = (evaluate_hand(B_bot), evaluate_hand(B_mid), evaluate_hand(B_top))
    else:
        B_vals = ((0, [0]),) * 3

    for i in range(3):
        w = compare_hands(A_vals[i], B_vals[i])
        if w == 1:
            A_pts += 1
            A_rows += 1
        elif w == 2:
            B_pts += 1
            B_rows += 1

    # scoop bonus
    if A_rows == 3:
        A_pts += 3
    if B_rows == 3:
        B_pts += 3

    return A_pts, B_pts

def table_scores_4p(piles4):
    """
    piles4: list length 4 of (top,mid,bot)
    returns total score per player = sum of pairwise heads-up scores
    """
    totals = [0, 0, 0, 0]
    for i in range(4):
        for j in range(i + 1, 4):
            pi, pj = score_heads_up(piles4[i], piles4[j])
            totals[i] += pi
            totals[j] += pj
    return totals