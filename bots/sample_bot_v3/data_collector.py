import numpy
from game.engine import new_game, apply_move
from bots.sample_bot_v3.encoding import encode_state
from bots.base import Bot
from game.moves import EndTurn
from typing import Callable
import time as t
from bots.sample_bot_v3.sample_bot import ValueModel,Sampling_Bot_V3
from bots.sample_bot_v3.trainer import train
import pickle
import shutil


#takes no args and returns a bot
def collect(time, bot_factory:Callable[[],Bot], eval_input)->tuple[numpy.ndarray,numpy.ndarray]:
    x,y = [],[]

    start = t.perf_counter()
    g=0

    while (t.perf_counter()-start)<time:
        g+=1
        if g%150==0:
            print(f"{t.perf_counter()-start:.2f}/{time}(s) Remaining")
        
        bot_a:Bot = bot_factory(eval_input=eval_input)
        bot_b:Bot = bot_factory(eval_input=eval_input)
        
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

def run_iterations(hours, iterations, bot_factory, data_path, model_path):
    seconds = hours*3600
    cycle_sec = seconds/iterations
    for i in range(iterations):
        print(f"CYCLE {i}/{iterations}\n-------------------------------------------------------------------")
        x_new, y_new = collect(cycle_sec,bot_factory,model_path)
        append_data(x_new,y_new,data_path)
        train(data_path,model_path)
        Sampling_Bot_V3._value_model_cache.pop(model_path,None)#avoid reuse of same sample ever iteration
        shutil.copy(model_path,f"model_iter_{i}.pkl")#shell utilities (command line stuff)

def append_data(x_new,y_new,data_path):
    try:
        d = numpy.load(data_path)
        combined_x = numpy.concatenate([d["X"],x_new],axis=0)
        combined_y = numpy.concatenate([d["Y"],y_new],axis=0)
    except FileNotFoundError:
        combined_x = x_new
        combined_y = y_new

    numpy.savez_compressed(data_path,X=combined_x,Y=combined_y)

if __name__=="__main__":
    import cProfile, pstats
    from game.engine import new_game
    from bots.sample_bot_v3.sample_bot import Sampling_Bot_V3


    training_data = "acc_data.npz"
    model = "current_model.pkl"
    shutil.copy("model-test.pkl",model)


    run_iterations(
        hours=2/60,
        iterations=2,
        bot_factory=Sampling_Bot_V3,
        data_path=training_data,
        model_path=model)

    d = numpy.load(training_data)
    y_all = d["Y"]
    print(f"total samples: {len(y_all)}")
    print(f"Final balance: {y_all.mean():.3f}")
