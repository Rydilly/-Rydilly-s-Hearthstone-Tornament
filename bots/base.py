from abc import ABC, abstractmethod
from game.state import GameState
from game.moves import Move

class Bot(ABC):
    @abstractmethod
    def pick_move(self, state:GameState)->Move:
        ...
        
    def observe(self, state, move):
        pass
    @property
    def name(self)->str:
        return self.__class__.__name__