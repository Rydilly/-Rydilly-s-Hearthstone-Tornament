import numpy
from game.engine import new_game, apply_move
from bots.sample_bot_v3.encoding import encode_state
from bots.base import Bot
from game.moves import EndTurn
from typing import Callable

#takes no args and returns a bot
def collect(n_games: int, bot_factory:Callable[[],Bot])->tuple[numpy.ndarray,numpy.ndarray]:
    x,y = [],[]
    
    for g in range(n_games):
        bot_a:Bot = bot_factory()
        bot_b:Bot = bot_factory()
        state = new_game()
        states_this_game =[]
        if g%2==0:
            bots=(bot_a,bot_b)
        else:
            bots=(bot_b,bot_a)

        while state.winner is None and state.turn_number<100:
            cp=state.current_player
            cb=bots[cp]
            ob=bots[1-cp]
            features = encode_state(state,cp)
            states_this_game.append((features,cp))

            move = cb.pick_move(state)
            apply_move(state,move)
            ob.observe(state,move)

        if state.winner==-1:
                continue
        for feats, p in states_this_game:
            game_result = 1 if state.winner==p else 0

            x.append(feats)
            y.append(game_result)
    return numpy.stack(x).astype(numpy.float32),numpy.array(y,dtype=numpy.float32)

if __name__=="__main__":
    from bots.aggro_bot import AgroBot

    n_games = 200
    x,y = collect(n_games,AgroBot)
    numpy.savez_compressed("training-data-test",X=x,Y=y)

    print("shapes:",x,y)
    print(f"balance: {y.mean():.3f}should be .5")
    print("total wins", int(y.sum()),"Total losses:", int(len(y)-y.sum()))
    print(f"Avg states per game: {len(y)/n_games:.1f}")