from .constants import HASH_PATH, PRIMES
import pickle

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


import importlib.resources as res

def load_lookup_tables():
    with res.files("poker_utils").joinpath(HASH_PATH).open("rb") as f:
        tables = pickle.load(f)
    return tables["flushes"], tables["unique5"], tables["pairs"]


def save_lookup_tables(flushes, unique5, pairs, path=HASH_PATH):

    with open(path, "wb") as f:
        pickle.dump({
            "flushes": flushes, 
            "unique5": unique5, 
            "pairs": pairs}, 
        f)
    print(f"Lookup tables saved to {path}")


def build_lookup_tables(path=HASH_PATH):

    flushes = {}
    unique5 = {}
    pairs   = {}

    # Generate all combinations of unique cards (no duplicate ranks, ascending order)
    # starts with (0,1,2,3,4), lowest combination
    from itertools import combinations
    all_bitmasks = []
    for bits in combinations(range(13), 5): # extract combination
        #eg (0,1,2,3,4), (0,1,2,3,5) ...
        mask = sum(1 << b for b in bits) # shift bit over based on rank, creates unique hash
        all_bitmasks.append(mask)

    # Sort descending, higher ranks first
    all_bitmasks.sort(reverse=True)

    straight_flush_rank = 1      # best possible hand
    flush_rank          = 323    # starts after straight flushes + quads + boats
    straight_rank       = 1600
    high_card_rank      = 6186

    straights = [
        0b1111100000000,   # A-K-Q-J-T  (broadway)
        0b0111110000000,   # K-Q-J-T-9
        0b0011111000000,   # Q-J-T-9-8
        0b0001111100000,   # J-T-9-8-7
        0b0000111110000,   # T-9-8-7-6
        0b0000011111000,   # 9-8-7-6-5
        0b0000001111100,   # 8-7-6-5-4
        0b0000000111110,   # 7-6-5-4-3
        0b0000000011111,   # 6-5-4-3-2
        0b1000000001111,   # A-5-4-3-2  (wheel)
    ]

    for mask in all_bitmasks:
        if mask in straights:
            flushes[mask] = straight_flush_rank   # straight flush
            unique5[mask] = straight_rank         # plain straight
            straight_flush_rank += 1              # descending means next straight flush is worse
            straight_rank       += 1
        else:
            flushes[mask] = flush_rank            # flush
            unique5[mask] = high_card_rank        # high card
            flush_rank     += 1
            high_card_rank += 1



    # generate every possible 5-card rank combo (with repetition allowed)

    hand_rank_counter = {
        "four_of_a_kind":  11,      # starts after straight flush
        "full_house":      167,     # starts after quads (with kickers)
        "three_of_a_kind": 1610,
        "two_pair":        2468,
        "one_pair":        3326,
    }

    def prime_product(ranks):
        result = 1
        for r in ranks:
            result *= PRIMES[r]
        return result

    def hand_type(ranks):
        counts = {}
        for r in ranks:
            counts[r] = counts.get(r, 0) + 1
        freq = sorted(counts.values(), reverse=True)
        if freq[0] == 4:                  return "four_of_a_kind"
        if freq[0] == 3 and freq[1] == 2: return "full_house"
        if freq[0] == 3:                  return "three_of_a_kind"
        if freq[0] == 2 and freq[1] == 2: return "two_pair"
        if freq[0] == 2:                  return "one_pair"
        return None

    # Generate all rank combos with repetition that form pair-type hands
    # sorted best-to-worst so rank assignments are ordered correctly
    from itertools import combinations_with_replacement

    pair_hands = []
    for ranks in combinations_with_replacement(range(13), 5):
        htype = hand_type(ranks)
        if htype: # not None
            pair_hands.append((ranks, htype)) 

    # Sort: by hand type priority, then by rank values descending
    type_order = {
        "four_of_a_kind": 0,
        "full_house": 1,
        "three_of_a_kind": 2,
        "two_pair": 3,
        "one_pair": 4
    }
    pair_hands.sort(key=lambda x: (type_order[x[1]], [-r for r in sorted(x[0], reverse=True)]))

    for ranks, htype in pair_hands:
        product = prime_product(ranks) # Unique hash
        pairs[product] = hand_rank_counter[htype]
        hand_rank_counter[htype] += 1

    save_lookup_tables(flushes, unique5, pairs, path)

    return flushes, unique5, pairs

if __name__ == '__main__':
    build_lookup_tables()



