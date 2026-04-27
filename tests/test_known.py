from random import randint, sample

from poker_utils.evaluation import *
from poker_utils.interface import *

#* Card bit representation
#*
#* Bit layout (32 bits per card):
#*  +--------+--------+--------+--------+
#*      AKQJT 98765432
#*  |xxxbbbbb|bbbbbbbb|cdhsrrrr|xxpppppp|
#*  +--------+--------+--------+--------+
#*
#*  p = prime number for rank (2,3,5,7,11,13,17,19,23,29,31,37,41)
#*  r = rank index (0–12)
#*  cdhs = suit bit flags
#*  b = rank bitmask (for detecting straights)

# Accepted card formats:
# 'As', 'Kh', '2d', '3c'
# ('2', 'c'), ('Q', 'h'), ('9', 's')
# (2, 'c'), (14, 'h'), (9, 's')
# (2, 0), (14, 2), (9, 3)
# where rank is an integer from 2-14 for 2-A and suit is an integer from 0-3 for c,d,h,s
def test_encoding():

    known_cards = [
        (0b00010000000000000010110000101001,  "ah","Ah","aH","AH", ("a","h"),("A","h"),("a","H"),("A","H"), (14,"h"),(14,"H"), (14, 2), ("a",2), ("A",2) ),
        (0b00001000000000000001101100100101,  "ks","Ks","kS","KS", ("k","s"),("K","s"),("k","S"),("K","S"), (13,"s"),(13,"S"), (13, 3), ("k",3), ("K",3) ),
        (0b00000001000000000100100000010111,  "td","Td","tD","TD", ("t","d"),("T","d"),("t","D"),("T","D"), (10,"d"),(10,"D"), (10, 1), ("t",1), ("T",1) ),
        (0b00000000000000011000000000000001,  "2c","2c","2C","2C", ("2","c"),("2","c"),("2","C"),("2","C"), (2 ,"c"),(2 ,"C"), (2,  0), ("2",0), ("2",0) ),
        (0b00000000001000000010010100001101,  "7h","7h","7H","7H", ("7","h"),("7","h"),("7","H"),("7","H"), (7 ,"h"),(7 ,"H"), (7,  2), ("7",2), ("7",2) ),
    ]
    # test encode_card with known cards
    for encoding, *group in known_cards:
        for card in group:
            assert encode_card(card) == encoding

    # test encode_hand with random cards
    card_inputs = [group[randint(1, len(group) - 1)] for group in known_cards]
    known_encodings = [encoding for encoding, *_ in known_cards]
    encoded_hand = encode_hand(card_inputs)

    assert isinstance(encoded_hand, list)
    assert encoded_hand == known_encodings

def test_hand_type():
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
    for hand, expected in known_hands:
        hand = encode_hand(hand)
        assert hand_type(hand) == expected

def test_hand_type_rank():
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
    for hand, expected in known_hands:
        hand = score5(encode_hand(hand))
        assert hand_type_score(hand) == expected

def test_score_hands():
    known_hands = [
            ["As", "Ks", "Qs", "Js", "Ts"],
            ["9c", "9d", "9h", "9s", "2d"],
            ["3c", "3d", "3h", "8s", "8d"],
            ["Ah", "Jh", "7h", "4h", "2h"],
            ["9c", "8d", "7h", "6s", "5c"],
            ["Qc", "Qd", "Qh", "2s", "9d"],
            ["5c", "5d", "9h", "9s", "2c"],
            ["6c", "6d", "2s", "9h", "Kc"],
            ["Ah", "Jd", "9c", "6s", "3d"],
    ]
    # Test that the hands are ranked correctly relative to each other.
    # By construction, known_hands[0] should beat all, ... last is worst.
    encoded_hands = [encode_hand(hand) for hand in known_hands]
    hand_scores = score_hands(*encoded_hands)
    for i in range(1, len(hand_scores)):
        # Lower score is better
        assert hand_scores[i-1] < hand_scores[i], (
            f"Hand {known_hands[i-1]} (score {hand_scores[i-1]}) "
            f"should rank better than {known_hands[i]} (score {hand_scores[i]})"
        )





