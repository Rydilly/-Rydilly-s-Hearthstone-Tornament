import random
from bots.base import Bot
from game.engine import legal_moves
from game.state import GameState
import game.moves as m
import game.cards as c




class ValueBot(Bot):
    """
    Priority
    1.lethal
    2.heal the highest attack friendly
    3.play most expensive minion
    4. kill a minion without dying
    5. face damage
    """
    def pick_move(self, state: GameState, moves = None):
        current = state.players[state.current_player]
        opponent = state.players[1-state.current_player] 
        if moves==None:
            moves = legal_moves(state)

        play_moves = [mv for mv in moves if isinstance(mv, m.PlayMinion)]
        attack_moves = [mv for mv in moves if isinstance(mv, m.Attack)]
        attack_hero_moves = [mv for mv in moves if isinstance(mv, m.AttackHero)]
        hero_power_moves = [mv for mv in moves if isinstance(mv, m.HeroPower)]

        #1.lethal checker
        total_dmg = 0
        for mv in attack_hero_moves:
            total_dmg+=current.board[mv.attacker_index].attack
        if total_dmg>=opponent.hp:
            return attack_hero_moves[0]
        
        #2.best heal  
        heal_move = self._best_heal(hero_power_moves, current)
        if heal_move is not None:
            return heal_move
        
        #3.most expensive minion(might want to try to use all mana later)
        if play_moves:
            return max(play_moves, key=lambda mv: c.CARD_DEFS[current.hand[mv.hand_index]].cost)
        
        #4.best trade
        trade = self._best_trade(attack_moves, current, opponent)
        if trade is not None:
            return trade

        #5.face dmg
        if attack_hero_moves:
            return attack_hero_moves[0]

        #6.any attack
        if attack_moves:
            return attack_moves[0]
        
        return m.EndTurn()


    def _best_heal(self, hero_power_moves, current):
        best = None
        best_attack = 0
        for mv in hero_power_moves:
            if not isinstance(mv.target, m.FriendlyMinion):
                continue
            minion = current.board[mv.target.index]
            if minion.max_health-minion.health<2:
                continue
            if minion.attack>best_attack:
                best = mv
                best_attack = minion.attack
        return best

    def _best_trade(self, attack_moves, current, opponent):
        """
        find attack where attacker survives and defender dies
        """
        for mv in attack_moves:
            attacker = current.board[mv.attacker_index]
            defender = opponent.board[mv.target_index]
            attacker_survives = attacker.health>defender.attack
            defender_dies = defender.health<attacker.attack
            if attacker_survives and defender_dies:
                return mv
        return None
        

                

