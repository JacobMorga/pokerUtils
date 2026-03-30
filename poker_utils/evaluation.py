from .constants import PRIMES, INT_RANK, INT_SUIT, SUIT_MASK
from .build import load_lookup_tables

FLUSHES, UNIQUE5, PAIRS = load_lookup_tables()

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

# rank: int from 2-14 for 2-A, suit 0,1,2,3 for c,d,h,s 
def encode_card(*args):

    if len(args) == 1: # Form 'As', 'Kh', '2d', '3c'
        card = args[0]
        if isinstance(card, str):
            rank = card[0].upper()
            suit = card[1].lower()
        else:
            raise ValueError('Invalid card format')

    elif len(args) == 2: 
        rank, suit = args
        if isinstance(rank, str) and isinstance(suit, str): # Form ('2', 'c'), ('Q', 'h'), ('9', 's')
            rank, suit = rank.upper(), suit.lower()
            
        elif isinstance(rank, int) and isinstance(suit, str): # Form (2, 'c'), (14, 'h'), (9, 's')
            rank, suit = INT_RANK[rank], suit.lower()

        elif isinstance(rank, int) and isinstance(suit, int): # Form (2, 0), (14, 2), (9, 3)
            rank, suit = INT_RANK[rank], INT_SUIT[suit]

        else:
            raise ValueError('Invalid card format')
    
    else:
        raise ValueError('Invalid card format')


    if rank not in '23456789TJQKA':
        raise ValueError('Invalid rank')
    if suit not in 'cdhs':
        raise ValueError('Invalid suit')
    rank = '23456789TJQKA'.index(rank)
    suit = SUIT_MASK[suit]

    prime     = PRIMES[rank]               # bits 0–5:   prime for rank
    rank_bits = rank << 8                  # bits 8–11:  rank as integer
    suit_bits = suit << 12                 # bits 12–15: suit bitmask
    rank_flag = (1 << rank) << 16         # bits 16–28: rank as positional bitmask

    return prime | rank_bits | suit_bits | rank_flag

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
            return hand_rankings[upper]
    
    return ValueError('Invalid hand rank')