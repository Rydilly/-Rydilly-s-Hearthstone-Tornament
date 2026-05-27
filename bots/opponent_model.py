from collections import Counter
from game.cards import CardName, STARTER_DECK
from game.moves import PlayMinion, EndTurn
from game.state import GameState

"""
on next version of this game make 1 class that tracks all the public knowledge of the game for both players
"""
class OpponentModel:
    def __init__(self):
        self.played: Counter[CardName] = Counter()
        self.unseen: Counter[CardName] = Counter(STARTER_DECK)
        self.weights:dict[CardName,float]= {card: 1.0 for card in self.unseen}

    def observe(self, state:GameState, move):

        #print(f"OBSERVE: cp={state.current_player}, MOVE={move}")

        match move:
            case PlayMinion(_,board_position):
                self.observe_play(state.players[state.current_player].board[board_position].card)
            case EndTurn():
                self._update_on_end_turn(state)
            case _:
                return
            
    def _update_on_end_turn(self, state:GameState):#NOTE: IF A CARD IS PLAYABLE AND THE OPP ENDS TURN WITH ENOUGH MANA TO PLAY IT BUT DOSNT THE LIKELYHOOD SHOULD DECREASE OR AT LEAST TRY THIS APPROACH LATER
        me = state.players[1-state.current_player]
        opponent = state.players[state.current_player]

        if opponent.hp<1:
            return
        if opponent.mana>1 and not CardName.DOOMSAYER in [mn.card for mn in opponent.board] and len(opponent.board)<7:#didnt play doomsayer
            pressure = (sum(mn.attack for mn in me.board)-sum(mn.attack for mn in opponent.board))/opponent.hp
            if pressure>0:
                f =  max(.1, 1.0-pressure)
                self.weights[CardName.DOOMSAYER]*=f
        else:
            return


    def observe_play(self, card: CardName)->None:

        #print(f"OBSERVING {card.name}, UNSEEN COUNT:{self.unseen[card]}")

        self.weights[card]=1#if opponent plays a card it resets our assumption of if it is in their hand
        assert self.unseen[card]>0, f"\nUNSEEN:{self.unseen}"#in current model we know whats in the opponents deck
        self.unseen[card]-=1    
        self.played[card]+=1

    def prob_card_in_hand(self, card: CardName, hand_size:int)->float:
        """
        Probability at least 1 copy of card is in hand
        """
        if self.unseen[card]==0:
            return 0
        amount_of_card = self.unseen[card]
        unseen_size = sum(self.unseen.values())
        not_yet_drawn_size = unseen_size-hand_size

        output = 1
        for i in range(amount_of_card):#chance of all card not being in hand
            output*= not_yet_drawn_size/unseen_size#chance of 1 being in deck
            not_yet_drawn_size-=1
            unseen_size-=1
        return (1-output)*self.weights[card] #inverse probability
    
    def expected_count_in_hand(self, card, hand_size)->float:
        """
        returns a float representing how many of card is in hand averaged over every possible scenariro
        """
        ammount_of_card = self.unseen[card]#i need better names
        unseen_size = sum(self.unseen.values())
        if unseen_size==0:
            return 0
        return ammount_of_card*hand_size/unseen_size
    
    



if __name__=="__main__":
    m = OpponentModel()

    print(sum(m.prob_card_in_hand(card,4) for card in m.unseen))#should be 4 (4 cars in hand prob of any card in hand). update I was wrong because duplicates so it should be less then hand size because there are instances of duplicates in hand 
    print(sum(m.expected_count_in_hand(card,4) for card in m.unseen))
    

    assert .26<m.prob_card_in_hand(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE,4)<.27
    #print(m.prob_card_in_hand(CardName.CLEANSING_CLERIC,4))
    assert .47<m.prob_card_in_hand(CardName.CLEANSING_CLERIC,4)<.48
    assert .26<m.prob_card_in_hand(CardName.BLOODMAGE_THALNOS,4)<.27
