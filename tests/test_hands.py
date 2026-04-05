from __future__ import annotations

import math
import random
from collections import Counter

from poker_utils.evaluation import *



def test_hand_type_known_examples():
    known_hands = [
        (["As", "Ks", "Qs", "Js", "Ts"], "straight_flush"),
        (["9c", "9d", "9h", "9s", "2d"], "four_of_a_kind"),
        (["3c", "3d", "3h", "8s", "8d"], "full_house"),
        (["Ah", "Jh", "7h", "4h", "2h"], "flush"),
        (["9c", "8d", "7h", "6s", "5c"], "straight"),
        (["Qc", "Qd", "Qh", "2s", "9d"], "three_of_a_kind"),
        (["5c", "5d", "9h", "9s", "2c"], "two_pair"),
        (["6c", "6d", "2s", "9h", "Kc"], "one_pair"),
        (["Ah", "Jd", "9c", "6s", "3d"], "high_card"),
    ]
    for set in known_hands:
        hand, expected = set
        hand = encode_hand(hand)
        assert hand_type(score_hand(hand)) == expected


def test_hand_type_distribution(n=1_000_000) -> None:
    """
    Monte Carlo test against known 5-card poker hand-type frequencies.

    Expected counts are for a uniformly random 5-card poker hand from a
    52-card deck (i.e., sampling without replacement).
    """
    # Deterministic test.
    rng = random.Random(0)

    # Known theoretical counts for 5-card poker (out of 2,598,960 total):
    # http://en.wikipedia.org/wiki/Probability_of_poker_hands
    expected_counts = {
        "straight_flush": 40,
        "four_of_a_kind": 624,
        "full_house": 3744,
        "flush": 5108,
        "straight": 10200,
        "three_of_a_kind": 54912,
        "two_pair": 123552,
        "one_pair": 1098240,
        "high_card": 1302540,
    }
    expected_total = 2598960

    ranks = "23456789TJQKA"
    suits = "cdhs"
    deck = [_ for _ in (encode_card(r + s) for r in ranks for s in suits)]

    observed = Counter()
    for _ in range(n):
        hand = rng.sample(deck, 5)
        observed[hand_type(evaluate(hand))] += 1

    # 1) Per-category sanity: within 6 sigma of expected count.
    # 2) Overall sanity: chi-square should be well within a reasonable range.
    chi_square = 0.0
    for hand_type_name, exp_count in expected_counts.items():
        exp = n * exp_count / expected_total
        obs = observed.get(hand_type_name, 0)

        # Use a normal approximation; with n=1e6 this is very stable.
        sigma = math.sqrt(exp)
        assert abs(obs - exp) <= 6.0 * sigma, (
            f"Hand type {hand_type_name}: observed {obs}, expected {exp:.1f}"
        )

        chi_square += (obs - exp) ** 2 / exp

    # df = 8 (9 categories - 1), mean=8, sd=sqrt(16)=4.
    # Chi-square > 30 is extremely unlikely under correct behavior.
    assert chi_square < 30.0
