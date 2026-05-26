from game.state import GameState
from bots.base import Bot
from bots.value_bot import ValueBot
from game.engine import legal_moves
from game.moves import Move, PlayMinion
from game.cards import CardName
from bots.opponent_model import OpponentModel

class Doomsayer_smart_bot(Bot):
    def __init__(self):
        self.default_brain = ValueBot()
        self.eyes = OpponentModel()
        
    def pick_move(self, state):
        op_board = state.players[1-state.current_player].board
        my_board = state.players[state.current_player].board

        doom_sayer_on_board = False
        for minion in op_board:
            if minion.card is CardName.DOOMSAYER:
                doom_sayer_on_board=True
                break
        if not doom_sayer_on_board:
            for minion in my_board:
                if minion.card is CardName.DOOMSAYER:
                    doom_sayer_on_board=True
                    break
        
        moves = legal_moves(state)
   
        enemy_total_dmg = sum(mn.attack for mn in state.players[1-state.current_player].board)
        my_total_dmg = sum(mn.attack for mn in state.players[state.current_player].board)
        
        alexstraz_in_hand=False

        if state.players[state.current_player].hp<15:
            for mv in moves:
                if (isinstance(mv,PlayMinion) 
                    and state.players[state.current_player].hand[mv.hand_index] is CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE):
                    return mv

        if enemy_total_dmg-my_total_dmg>5:
            for mv in moves:
                match mv:
                    case PlayMinion(idx,_):
                        if state.players[state.current_player].hand[idx] is CardName.DOOMSAYER:
                            return mv
                    case _:
                        pass

        if doom_sayer_on_board or .95<self.eyes.prob_card_in_hand(CardName.DOOMSAYER, len(state.players[1-state.current_player].hand)):
            moves = [mv for mv in moves if not isinstance(mv,PlayMinion)]

        moves = [mv for mv in moves 
                 if not (isinstance(mv, PlayMinion) 
                         and state.players[state.current_player].hand[mv.hand_index] in (CardName.DOOMSAYER, CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE))]
        return self.default_brain.pick_move(state, moves)


    def observe(self, state, move):
        self.eyes.observe(state,move)

if __name__ == "__main__":
    from play import run_tournament
    from bots.aggro_bot import AgroBot
    print(run_tournament(Doomsayer_smart_bot, ValueBot, n_games=1000))
                
        

                
    

