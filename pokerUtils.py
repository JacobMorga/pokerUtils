from build import *

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
#*  b = rank bitmask (for detecting straights/flushes)

def encode_card(rank, suit):

    prime     = PRIMES[rank]               # bits 0–5:   prime for rank
    rank_bits = rank << 8                  # bits 8–11:  rank as integer
    suit_bits = suit << 12                 # bits 12–15: suit bitmask
    rank_flag = (1 << rank) << 16         # bits 16–28: rank as positional bitmask

    return prime | rank_bits | suit_bits | rank_flag


load_lookup_tables()
def evaluate(cards):

    rank_mask = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
    suit_mask = cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000

    # handles both flushes and straight flushes
    if bool(suit_mask):
        return FLUSHES[rank_mask]   

    # handles straights and high cards
    if rank_mask in UNIQUE5:
        return UNIQUE5[rank_mask]   

    # handles pairs, set, boats, quads
    prime_product = 1
    for card in cards:
        prime_product *= card & 0x3F    # extract bits 0–5 (the prime)

    return PAIRS[prime_product]

def hand_type (rank):
    hand_rankings = {
        1    : 'straight_flush',     
        11   : 'four_of_a_kind',      
        167  : 'full_house',     
        323  : 'flush',   
        1600 : 'straight',
        1610 : 'three_of_a_kind',
        2468 : 'two_pair',
        3326 : 'one_pair',
        6186 : 'high_card',
    }

    boundaries = hand_rankings.keys()

    for upper in reversed(boundaries):
        if rank <= upper:
            return hand_rankings(upper)
    
    return ValueError('Invalid hand rank')