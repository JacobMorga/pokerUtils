from poker_utils.evaluation import encode_card, evaluate, hand_type

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

def test_straight_flush():
    hand = ['As','Ks','Qs','Js','Ts']
    hand = [encode_card(*card) for card in hand]
    assert hand_type(evaluate(hand)) == 'straight_flush'
