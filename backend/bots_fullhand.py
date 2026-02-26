# backend/bots_fullhand.py
from typing import List, Tuple
from ofcp_core import evaluate_hand, valid_order, Card

RANKS = "23456789TJQKA"

def _rv(r): return RANKS.index(r) + 2

def arrange_greedy(cards13: List[Card]) -> Tuple[List[Card], List[Card], List[Card]]:
    """
    Fast greedy arrangement into (top3, mid5, bot5).
    Idea:
      - sort high->low
      - build bottom/middle first
      - keep top relatively weak (low cards) unless it forms a pair/trips
    """
    cards = sorted(cards13, key=lambda c: _rv(c.rank), reverse=True)

    top, mid, bot = [], [], []

    def place(card):
        # legal piles
        opts = []
        if len(top) < 3: opts.append("top")
        if len(mid) < 5: opts.append("mid")
        if len(bot) < 5: opts.append("bot")

        # heuristic scoring
        best = None
        best_sc = -1e9
        for p in opts:
            t = top[:] ; m = mid[:] ; b = bot[:]
            if p == "top": t.append(card)
            if p == "mid": m.append(card)
            if p == "bot": b.append(card)

            # base preference: bot > mid > top
            sc = {"bot": 1.0, "mid": 0.5, "top": 0.0}[p]

            # penalty for strong top cards
            if p == "top" and _rv(card.rank) >= 11:
                sc -= 1.0

            # prefer pairs/trips in bot/mid
            if p in ("bot", "mid"):
                pile = b if p == "bot" else m
                ranks = [c.rank for c in pile]
                if ranks.count(card.rank) == 2:  # makes trips
                    sc += 1.2
                elif ranks.count(card.rank) == 1:  # makes pair
                    sc += 0.6

            # ordering safety bonus (partial)
            # (if complete, enforce)
            if len(t) == 3 and len(m) == 5 and len(b) == 5:
                if valid_order(t, m, b):
                    sc += 2.0
                else:
                    sc -= 4.0
            else:
                # mild bonus if bot strength >= mid >= top so far
                sc += 0.1 if evaluate_hand(b or [card]) >= evaluate_hand(m or [card]) else 0.0

            if sc > best_sc:
                best_sc = sc
                best = p

        if best == "top": top.append(card)
        elif best == "mid": mid.append(card)
        else: bot.append(card)

    for c in cards:
        place(c)

    # if foul, attempt quick fix: swap some cards between piles
    if not valid_order(top, mid, bot):
        # try a few swaps
        for _ in range(200):
            # swap random between mid/bot or top/mid
            import random
            a, b_ = random.choice([("mid", "bot"), ("top", "mid")])
            A = top if a == "top" else (mid if a == "mid" else bot)
            B = top if b_ == "top" else (mid if b_ == "mid" else bot)
            if not A or not B:
                continue
            i = random.randrange(len(A))
            j = random.randrange(len(B))
            A[i], B[j] = B[j], A[i]
            if valid_order(top, mid, bot):
                break
            # swap back
            A[i], B[j] = B[j], A[i]

    return top, mid, bot