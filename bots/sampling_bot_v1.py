from bots.base import Bot
from bots.opponent_model import OpponentModel
import random 
from game.state import GameState
import copy
from bots.value_bot import ValueBot
from game.moves import Move, EndTurn, PlayMinion
from game.engine import apply_move, legal_moves
from game.cards import CardName
import math
from bots.sample_hand import Sample_Hand



class Sampling_Bot(Bot):
    def __init__(self, sim_opp:Bot = ValueBot()):
        self.eyes = OpponentModel()
        self.sim_opp = sim_opp

    def pick_move(self, state:GameState):
        #print(self, state)
        moves = legal_moves(state)

        me = state.players[state.current_player]
        opp = state.players[1-state.current_player]
        opp_idx = 1-state.current_player
        my_idx = state.current_player
        best_move = (EndTurn(), -100000)

        for mv in moves:
            
            scores = []
            for _ in range(math.ceil(len(self.eyes.unseen)/max(1,len(opp.hand)))):
                sim_state = apply_move(state,mv)
                sh = Sample_Hand(self.eyes.unseen)
                sh.draw(len(opp.hand))
                sim_state = self.replace_opp_hand(sim_state, sh.hand ,opp_idx)
                sim_state = self.sim_opps_turn(sim_state)
                scores.append(self.evaluate(sim_state, my_idx))
            avg_score = (sum(scores)/len(scores))

            if avg_score>best_move[1]:
                best_move=(mv,avg_score)
        """
        #print(f"best move: {best_move[0]}")
        if isinstance(best_move[0],PlayMinion):
            if me.hand[best_move[0].hand_index] in (CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE, CardName.DOOMSAYER):
                print(f"({opp.hp})\n<{opp.board}>\n\n{me.board}\n{me.hp}\n\nPlayCard:{me.hand[best_move[0].hand_index].name}")
        """
        return best_move[0]
        

    def replace_opp_hand(self, game_state: GameState, new_hand, opp_idx:int):
        new_game_state = copy.deepcopy(game_state)
        new_game_state.players[opp_idx].hand =new_hand
        return new_game_state
    
    def sim_opps_turn(self, sim_state:GameState)->GameState:
        cur_move = None
        while not isinstance(cur_move, EndTurn) and (sim_state.winner is None):
            cur_move = self.sim_opp.pick_move(sim_state)
            sim_state = apply_move(sim_state, cur_move)   
        return sim_state

    def evaluate(self, state: GameState, my_idx:int)->float:
        me = state.players[my_idx]
        opp = state.players[1-my_idx]
        score = (
            1* (me.hp-opp.hp)+
            2*(sum(m.attack for m in me.board)-sum(m.attack for m in opp.board))+
            1*(sum(m.health for m in me.board)-sum(m.health for m in opp.board))+
            .5*(len(me.hand)-len(opp.hand))
        )
        if me.hp<1:
            score-=1000
        if opp.hp<1:
            score+=1000

        return score



if __name__=="__main__":

    from game.engine import new_game
    from bots.value_bot import ValueBot

    s = Sampling_Bot()
    state = new_game(seed=42)
    fake_hand = Sample_Hand()
    fake_hand.draw(4)

    new_state=s.replace_opp_hand(state, fake_hand, opp_idx=1)

    print("new state opp hand:", new_state.players[1].hand)
    print("og opp hand:", state.players[1].hand)

  
    #print(s.sample_hand(4))

    print("\n\n")
    s = Sampling_Bot()
    v = ValueBot()
    state = new_game(seed=42)

    print(f"Before: {state.players[0].hp, state.players[1].hp, state.current_player}")
    
    after = s.sim_opps_turn(state)
    print(f"after: {after.players[0].hp, state.players[1].hp, after.current_player}")

    print("\n\n")

    s = Sampling_Bot()
    state = new_game(seed=42)
    print(s.evaluate(state, my_idx=0))
    state.players[1].hp=0
    assert s.evaluate(state, my_idx=0)>999, f"{s.evaluate(state, my_idx=0)}"

