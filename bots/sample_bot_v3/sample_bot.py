from bots.base import Bot
from bots.opponent_model import OpponentModel
from game.state import GameState, PlayerState
from bots.value_bot import ValueBot
from game.moves import Move, EndTurn, PlayMinion
from game.engine import apply_move, legal_moves, _start_turn
from game.cards import CardName
import math
from bots.sample_hand import Sample_Hand
from game.undo import undo_move, Op as UndoOp
import math
from bots.lethal_bot import Lethal_Bot
import numpy as np
import pickle
from bots.sample_bot_v3.encoding import encode_state
from sklearn.linear_model import LogisticRegression




class Sampling_Bot_V3(Bot):
    _value_model_cache = {}

    def __init__(self, depth = 2, opp_data = None, my_data = None, in_sim=False,eval_input=None):
        self.opp_data = OpponentModel() if opp_data is None else opp_data
        self.my_data = OpponentModel() if my_data is None else my_data
        self.depth=depth
        self.in_sim = in_sim
        self.lethal_finder = Lethal_Bot()
        self.eval_input=eval_input
        
        path = eval_input if eval_input is not None else "model-test.pkl"#caching various ValueModels to avoid re opening the same file a ton
        if path not in Sampling_Bot_V3._value_model_cache:
            Sampling_Bot_V3._value_model_cache[path]=ValueModel(path)
        self.ValueModel = Sampling_Bot_V3._value_model_cache[path]


    def observe(self, state, move):
        self.opp_data.observe(state,move)

    def pick_move(self, state:GameState):
        #print(self, state)
        moves = legal_moves(state)

        if not self.in_sim:
            lethal_combo = self.lethal_finder.find_lethal(state)#heavy call. dont want to call it when its not needed
            if lethal_combo:
                #print(F"LETHAL FOUND!! \nlethal combo:{lethal_combo}")
                return lethal_combo[0]

        me = state.players[state.current_player]
        opp = state.players[1-state.current_player]
        opp_idx = 1-state.current_player
        my_idx = state.current_player
        best_move = (EndTurn(), -100000)

        if self.depth==2:
            #r = range(math.ceil(len(self.opp_data.unseen.values())/max(1,len(opp.hand)*3)))
            r=range(3)
        else:
            r=range(1)
        for mv in moves:#find the move with the highest average score
            
            scores = []
            for _ in r:
                undo = apply_move(state,mv)
                sh = Sample_Hand(self.opp_data.unseen, self.opp_data.weights)
                sh.draw(len(opp.hand))
                self.replace_opp_hand(state,sh.hand,opp_idx,undo)
                undo.extend(apply_move(state,EndTurn()))
                self.sim_opps_turn(state,undo)


                
                score = -math.inf
                mv2_legal = legal_moves(state)
                if not mv2_legal or state.winner is not None:
                    score = self.evaluate(state, my_idx)
                else:    
                    #print(f"cp={state.current_player}, my_idx={my_idx}, board={[m.card for m in state.players[my_idx].board]}")
                    for mv2 in mv2_legal:
                        tmp_undo = (apply_move(state,mv2)) 

                        tmp_undo.extend(apply_move(state,EndTurn()))

                        sc = self.evaluate(state,my_idx)
                        if sc>score:
                            score = sc
                        undo_move(state,tmp_undo)
                           
                scores.append(score)
                undo_move(state, undo)
                

                
            avg_score = (sum(scores)/len(scores))

            if avg_score>best_move[1]:
                best_move=(mv,avg_score)
        """
        #print(f"best move: {best_move[0]}")
        if isinstance(best_move[0],PlayMinion):
            if me.hand[best_move[0].hand_index] in (CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE, CardName.DOOMSAYER):
                print(f"({opp.hp})\n<{opp.board}>\n\n{me.board}\n{me.hp}\n\nPlayCard:{me.hand[best_move[0].hand_index].name}")
        """
        if not self.in_sim:#update my data 
            if isinstance(best_move[0], PlayMinion):
                card = me.hand[best_move[0].hand_index]
                self.my_data.observe_play(card)
            elif isinstance(best_move[0], EndTurn):
                self.my_data._update_on_end_turn(state)

        return best_move[0]#return mv with the highest avg rating
        

    def replace_opp_hand(self, game_state: GameState, new_hand, opp_idx:int, undo:list):
        opp = game_state.players[opp_idx]
        
        undo.append((UndoOp.SET_PLAYER_HAND,opp_idx,opp.hand))
        game_state.players[opp_idx].hand =new_hand

        return 
    
    def sim_opps_turn(self, sim_state:GameState, undo:list)->GameState:
        cur_move = None
        temp_brain = Sampling_Bot_V3(depth=self.depth-1, opp_data=self.my_data, my_data=self.opp_data, in_sim=True, eval_input=self.eval_input)
        while not isinstance(cur_move, EndTurn) and (sim_state.winner is None) and not (self.depth<1):
            cur_move = temp_brain.pick_move(sim_state)
            undo.extend(apply_move(sim_state, cur_move))#apply_move returns a undo:list  
        return 

    def evaluate(self, state: GameState, my_idx:int)->float:        
        """
        todo:
        add phase based eval. ie tempo favored early, resources favored leta, near lethal burst favored
        mana efficency
        log scaling on hp 30 to 29 is nothing, 3 to.2 is huge
        archetype awareness
        threat projection
        opp board value can increase score if i have a board clear
        delayed value, conditional value, swing potential
        """
        me = state.players[my_idx]
        opp = state.players[1-my_idx]

        if me.hp<1:
            return -10000
        if opp.hp<1:
            return 10000
        
        return self.ValueModel.score(state,my_idx)

class ValueModel:
    def __init__(self,eval_input="model-test.pkl"): 
        with open(eval_input,"rb") as f:
            model:LogisticRegression = pickle.load(f)
        self.weights = model.coef_[0]
        self.bias = model.intercept_[0]

    def score(self, state, my_idx):
        features = encode_state(state,my_idx)
        z = features @self.weights + self.bias#@ is vector mult then c to make linear scaling of any heuristid. resutlt is -50 to 50
        return 1.0/(1.0+np.exp(-z))#applies z to the -z power. larger z approaches 0 smaller approaches 1 because z lowest is 0
        

        

if __name__=="__main__":
    from collections import Counter
    from game.engine import new_game
    from bots.value_bot import ValueBot
    from game.cards import STARTER_DECK
    import time
    import cProfile, pstats

    

    vm = ValueModel("model-test.pkl")
    state = new_game(seed=42)
    print(f"P0 win prob at start: {vm.score(state,0):.3f}")
    print(f"P1 win prob at start: {vm.score(state,1):.3f}")

    state.players[1].hp=5
    state.players[1].hand.pop()
    print(f"P0 win prob at start: {vm.score(state,0):.3f}")
    print(f"P1 win prob at start: {vm.score(state,1):.3f}")