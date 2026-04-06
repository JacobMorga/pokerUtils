from .build import load_lookup_tables

FLUSHES, UNIQUE5, PAIRS = load_lookup_tables()


def score5(*cards): # return a score for a 5 card hand

    cards = list(cards)

    rank_mask = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
    suit_mask = cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000

    # handles both flushes and straight flushes
    if bool(suit_mask): # true if not 0x0000
        return FLUSHES[rank_mask]   

    # handles straights and high cards
    if rank_mask in UNIQUE5:
        return UNIQUE5[rank_mask]   

    # handles pairs, set, boats, quads
    prime_product = 1
    for card in cards:
        prime_product *= card & 0x3F    # extract bits 0–5 (the prime)
    return PAIRS[prime_product]

def score_hands(*hands):

    hands = list(hands) # tupules, list, multiple inputs
    return [score5(hand) for hand in hands]

def sort_hands(*hands):

    scores = score_hands(hands)
    indexed = list(enumerate(scores))  # [(0, scr1), (1, scr2), ...]
    return indexed.sort(key=lambda x: x[1])

    
    



