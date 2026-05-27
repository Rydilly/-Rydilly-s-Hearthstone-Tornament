from bots.base import Bot
from bots.opponent_model import OpponentModel
from game.state import GameState
from bots.value_bot import ValueBot
from game.moves import Move, EndTurn, PlayMinion
from game.engine import apply_move, legal_moves
from game.cards import CardName
import math
from bots.sample_hand import Sample_Hand
from game.undo import undo_move, Op as UndoOp
import math
from bots.lethal_bot import Lethal_Bot




class Sampling_Bot_V2(Bot):
    def __init__(self, depth = 2, opp_data = None, my_data = None, in_sim=False):
        self.opp_data = OpponentModel() if opp_data is None else opp_data
        self.my_data = OpponentModel() if my_data is None else my_data
        self.depth=depth
        self.in_sim = in_sim
        self.lethal_finder = Lethal_Bot()


    def observe(self, state, move):
        self.opp_data.observe(state,move)

    def pick_move(self, state:GameState):
        #print(self, state)
        moves = legal_moves(state)

        if not self.in_sim:
            lethal_combo = self.lethal_finder.find_lethal(state)#heavy call. dont want to call it when its not needed
            if lethal_combo:
                print(F"LETHAL FOUND!! \nlethal combo:{lethal_combo}")
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
        for mv in moves:
            
            scores = []
            for _ in r:
                undo = apply_move(state,mv)
                sh = Sample_Hand(self.opp_data.unseen, self.opp_data.weights)
                sh.draw(len(opp.hand))
                self.replace_opp_hand(state,sh.hand,opp_idx,undo)
                self.sim_opps_turn(state,undo)
    
                
                score = -math.inf
                mv2_legal = legal_moves(state)
                if not mv2_legal or state.winner is not None:
                    score = self.evaluate(state, my_idx)
                else:    
                    for mv2 in mv2_legal:
                        tmp_undo = apply_move(state,mv2) 
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
        if not self.in_sim:
            if isinstance(best_move[0], PlayMinion):
                card = me.hand[best_move[0].hand_index]
                self.my_data.observe_play(card)
            elif isinstance(best_move[0], EndTurn):
                self.my_data._update_on_end_turn(state)

        return best_move[0]
        

    def replace_opp_hand(self, game_state: GameState, new_hand, opp_idx:int, undo:list):
        opp = game_state.players[opp_idx]
        
        undo.append((UndoOp.SET_PLAYER_HAND,opp_idx,opp.hand))
        game_state.players[opp_idx].hand =new_hand

        return 
    
    def sim_opps_turn(self, sim_state:GameState, undo:list)->GameState:
        cur_move = None
        temp_brain = Sampling_Bot_V2(depth=self.depth-1, opp_data=self.my_data, my_data=self.opp_data, in_sim=True)
        while not isinstance(cur_move, EndTurn) and (sim_state.winner is None) and not (self.depth<1):
            cur_move = temp_brain.pick_move(sim_state)
            undo.extend(apply_move(sim_state, cur_move))#apply_move returns a undo:list   
        return 

    def evaluate(self, state: GameState, my_idx:int)->float:
        me = state.players[my_idx]
        opp = state.players[1-my_idx]
        me_m_atk=0
        opp_m_atk=0
        me_m_hp=0
        opp_m_hp=0

        for mn in me.board:
            me_m_atk+=mn.attack
            me_m_hp+=mn.health
        for mn in opp.board:
            opp_m_atk+=mn.attack
            opp_m_hp+=mn.health

        score = (
            1* (me.hp-opp.hp)+
            2*(me_m_atk-opp_m_atk)+
            1*(me_m_hp-opp_m_hp)+
            .5*(len(me.hand)-len(opp.hand))
        )
        if me.hp<1:
            score-=1000
        if opp.hp<1:
            score+=1000

        return score



if __name__=="__main__":
    from collections import Counter
    from game.engine import new_game
    from bots.value_bot import ValueBot
    from game.cards import STARTER_DECK
    import time
    import cProfile, pstats

    
    
    s = Sampling_Bot_V2()
    state = new_game(seed=42)
    #fake_hand = Sample_Hand(Counter(STARTER_DECK))
    #fake_hand.draw(4)
    sUndo = []

    profiler = cProfile.Profile()
    profiler.enable()
    s.pick_move(state)
    profiler.disable()
    pstats.Stats(profiler).sort_stats('cumulative').print_stats(20)

  
    #print(s.sample_hand(4))

    print("\n\n")
    s = Sampling_Bot_V2()
    v = ValueBot()
    state = new_game(seed=42)
    undo = []

    print(f"Before: {state.players[0].hp, state.players[1].hp, state.current_player}")
    
    s.sim_opps_turn(state,undo)
    print(f"after: {state.players[0].hp, state.players[1].hp, state.current_player}")

    print("\n\n")

    s = Sampling_Bot_V2()
    state = new_game(seed=42)
    print(s.evaluate(state, my_idx=0))
    state.players[1].hp=0
    assert s.evaluate(state, my_idx=0)>999, f"{s.evaluate(state, my_idx=0)}"

    print(s.pick_move(state))
    print("\n\n")

    # midgame test
    state = new_game(seed=42)
    v = ValueBot()
    for _ in range(20):
        if state.winner is not None: break
        move = v.pick_move(state)
        apply_move(state, move)

    print(state.render())
    print(f"opp hand size: {len(state.players[1-state.current_player].hand)}")

    import time
    s = Sampling_Bot_V2()
    start = time.perf_counter()
    mv = s.pick_move(state)
    print(f"midgame pick_move: {time.perf_counter() - start:.2f}s")
    print(f"picked: {mv}\n\n")

    import cProfile, pstats
    from bots.sampling_bot_V2 import Sampling_Bot_V2
    from bots.value_bot import ValueBot
    from game.engine import new_game, apply_move

    bot = Sampling_Bot_V2()
    state = new_game(seed=42)
    v = ValueBot()
    for _ in range(20):
        if state.winner is not None: break
        apply_move(state, v.pick_move(state))

    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(5):
        bot.pick_move(state)
    profiler.disable()
    pstats.Stats(profiler).sort_stats('cumulative').print_stats(25)
