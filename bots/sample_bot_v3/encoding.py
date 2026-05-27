import numpy
from game.state import GameState, PlayerState



def encode_state(g_state:GameState, player_idx)->numpy.ndarray:
    me:PlayerState = g_state.players[player_idx]
    opp:PlayerState = g_state.players[1-player_idx]
    
    features = [
        me.hp,
        opp.hp,
        me.hp-opp.hp,
        me.mana,
        me.max_mana,
        opp.max_mana,
        len(me.hand),
        len(opp.hand),
        len(me.deck),
        len(opp.deck),
        me.fatigue_counter,
        opp.fatigue_counter,
        me.hero_power_power,
        1.0 if me.hero_power_used else 0.0,
        me.alexstrasza_guardian_of_life_charges,
        g_state.turn_number
    ]
    features.extend(encode_minions(me))
    features.extend(encode_minions(opp))
    return numpy.array(features,dtype=numpy.float32)

def encode_minions(p_state:PlayerState)->list[float]:
        """
        makes vectors representing all minions on players board
        """

        features = []

        for mn in p_state.board:
            features.append(mn.attack)
            features.append(mn.health)
            features.append(mn.max_health)
            features.append(1.0 if mn.taunt else 0.0)
            features.append(1.0 if mn.can_attack else 0.0)
            
        while len(features)<(7*5):    
            features.append(0.0)

        return features

if __name__=="__main__":
    from game.engine import new_game
     
    state = new_game(seed=42)
    f:numpy.ndarray = encode_state(state,0)
    print(f"shape:{f.shape}\ndtype:{f.dtype}\nvalues:{f}")


