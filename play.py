from game.engine import new_game, apply_move, legal_moves
from game.state import GameState
from bots.base import Bot
from game.moves import EndTurn

def play_game(bot_0: Bot, bot_1: Bot, max_turns: int=100, verbose: bool=False)->int:
    state = new_game()
    bots = (bot_0,bot_1)

    turn_count = 0
    while state.winner is None and turn_count<max_turns * 50:
        current_bot = bots[state.current_player]
        other_bot = bots[1-state.current_player]
        move = current_bot.pick_move(state)
        if isinstance(move, EndTurn):
            turn_count+=1
            print(turn_count)

        if verbose:
            print(f"P{state.current_player} ({current_bot.name}): {move}")

        state = apply_move(state, move)
        other_bot.observe(state, move)

        if turn_count%50==0:
            print(f"{turn_count}, winner={state.winner}, p0_hp:{state.players[0].hp}, p1_hp:{state.players[1].hp}")
    return state.winner if state.winner is not None else -1


def run_tournament(bot_a_factory, bot_b_factory, n_games: int = 100)->dict:
    wins = {0:0,1:0,-1:0}
    for i in range(n_games):
        print(f"Game {i} processing")
        if i%2==0:
            winner = play_game(bot_b_factory(), bot_a_factory())
            if winner==0:
                wins[1]+=1
            elif winner==1:
                wins[0]+=1
            else:
                wins[-1]+=1
        else:
            winner = play_game(bot_a_factory(), bot_b_factory())
            if winner==0:
                wins[0]+=1
            elif winner==1:
                wins[1]+=1
            else:
                wins[-1]+=1


    total = n_games
    return{
        "bot_a_winrate":wins[0]/total,
        "bot_b_winrate":wins[1]/total,
        "tie_rate":wins[-1]/total
    }





def main():
    state = new_game(seed=42)
    bots = (RandomBot(), RandomBot())

    while state.winner is None:
        print(state.render())
        bot = bots[state.current_player]
        move = bot.pick_move(state)
        print(f"->{move}\n")
        state = apply_move(state,move)
    
    #print(state)
    print(f"\nWinner: P{state.winner}")


if __name__=="__main__":
    from bots.random_bot import RandomBot
    from bots.value_bot import ValueBot
    from bots.aggro_bot import AgroBot
    from bots.lethal_bot import Lethal_Bot
    from bots.doomsayer_smart_bot import Doomsayer_smart_bot as doom
    import time as t
    from bots.sampling_bot_v1 import Sampling_Bot
    from bots.sampling_bot_V2 import Sampling_Bot_V2


    

    #main()
    l = Lethal_Bot()
    a = AgroBot()
    #play_game(a,l,verbose=True)



    n_games = 1
    starting_cache_1 = len(Lethal_Bot.move_cache)


    clock = t.perf_counter()
    print(run_tournament(ValueBot,Sampling_Bot_V2,n_games))
    avg_time_1 = (t.perf_counter()-clock)/n_games
    print(f"AVG: {avg_time_1}'s per game")

"""
    starting_cache_2= len(Lethal_Bot.move_cache)
    clock = t.perf_counter()
    print(run_tournament(ValueBot,Lethal_Bot,n_games))
    avg_time_2 = (t.perf_counter()-clock)/n_games

    print(f"AT CACHE SIZE: {starting_cache_1} AVG_TIME: {avg_time_1}'s per game")
    print(f"AT CACHE SIZE: {starting_cache_2} AVG_TIME: {(t.perf_counter()-clock)/n_games}'s per game")
    print(f"CACHE SIZE IS NOW{len(Lethal_Bot.move_cache)}")

"""
