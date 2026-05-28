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
        if verbose:
            print(f"P{state.current_player} ({current_bot.name}): {move}")
        if isinstance(move, EndTurn):
            turn_count+=1
            print(f"TURN_COUNT:{turn_count}")
            if verbose:
                print(f"{state.players[1].hp}\n{[(m.attack,m.health) for m in state.players[1].board]}\n\n{[(m.attack,m.health) for m in state.players[0].board]}\n{state.players[0].hp}\n-------------------------------------------------------")
        

        apply_move(state, move)
        other_bot.observe(state, move)

        #print(f"after move hand:{state.players[1-state.current_player].hand}")

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
        print(f"bot_a_winrate:{wins[0]/n_games},\nbot_b_winrate:{wins[1]/n_games},\ntie_rate:{wins[-1]/n_games}")

    return{
        "bot_a_winrate":wins[0]/n_games,
        "bot_b_winrate":wins[1]/n_games,
        "tie_rate":wins[-1]/n_games
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
    from bots.sampling_bot_V2 import Sampling_Bot_V2
    from bots.sample_bot_v3.sample_bot import Sampling_Bot_V3

    

    #main()
    l = Lethal_Bot()
    a = AgroBot()
    d = doom()

    #play_game(a,l,verbose=True)



    n_games = 200
    starting_cache_1 = len(Lethal_Bot.move_cache)

    """
    clock = t.perf_counter()
    result_1 = run_tournament(Sampling_Bot_V2,ValueBot,n_games)
    avg_time_1 = (t.perf_counter()-clock)/n_games
    print(f"AVG: {avg_time_1}'s per game")

    clock = t.perf_counter()
    result_2 = run_tournament(Sampling_Bot_V2,AgroBot,n_games)
    avg_time_2 = (t.perf_counter()-clock)/n_games
    print(f"AVG: {avg_time_2}'s per game")
    """

    
    clock = t.perf_counter()
    result_3 = run_tournament(Sampling_Bot_V3,doom,n_games)
    avg_time_3 = (t.perf_counter()-clock)/n_games
    print(f"AVG: {avg_time_3}'s per game\nresults:{result_3}")

    #print(f"\n{avg_time_1}\n{result_1}\n\n{avg_time_2}\n{result_2}\n\n{avg_time_3}\n{result_3}")
    
    

"""
    starting_cache_2= len(Lethal_Bot.move_cache)
    clock = t.perf_counter()
    print(run_tournament(ValueBot,Lethal_Bot,n_games))
    avg_time_2 = (t.perf_counter()-clock)/n_games

    print(f"AT CACHE SIZE: {starting_cache_1} AVG_TIME: {avg_time_1}'s per game")
    print(f"AT CACHE SIZE: {starting_cache_2} AVG_TIME: {(t.perf_counter()-clock)/n_games}'s per game")
    print(f"CACHE SIZE IS NOW{len(Lethal_Bot.move_cache)}")

"""
