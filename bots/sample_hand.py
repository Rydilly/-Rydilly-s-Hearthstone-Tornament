from collections import Counter
import random
import copy
from game.state import cards

class Sample_Hand():
    def __init__(self, unseen:Counter, weights = None):
        self.unseen= unseen.copy()#shallow copy is fine because the keys are immutable and the keys are ints which are also immutable
        self.hand=[]
        self.weights = [1]*len(self.unseen) if weights is None else weights

    def draw(self, n_cards=1):
        pool:list[cards.CardName] = list(self.unseen.elements())
        for _ in range(n_cards):
            if sum(self.unseen.values())<1:#cant use len because counter still holds items when the counter ==0
                break
            
            w = [self.weights[c] for c in pool]

            next_card_idx = random.choices(range(len(pool)),weights=w,k=1)[0]#could probably just draw all cards i need in future
            next_card = pool.pop(next_card_idx)
            self.unseen[next_card]-=1
            self.hand.append(next_card)
        return
    
if __name__=="__main__":
    from game.cards import STARTER_DECK
    sh = Sample_Hand(Counter(STARTER_DECK))
    sh.draw(4)
    print(sum(sh.unseen.values()))#11 cards in deck
    sh.draw(1)
    print(sh.hand)#should be 5
    print(sum(sh.unseen.values()))#should be 10

