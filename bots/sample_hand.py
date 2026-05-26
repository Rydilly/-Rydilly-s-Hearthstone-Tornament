from collections import Counter
import random
import copy

class Sample_Hand():
    def __init__(self, unseen:Counter):
        self.unseen= unseen.copy()#shallow copy is fine because the keys are immutable and the keys are ints which are also immutable
        self.hand=[]

    def draw(self, n_cards=1):
        for _ in range(n_cards):
            if sum(self.unseen.values())<1:#cant use len because counter still holds items when the counter ==0
                break
            next_card = random.choice(list(self.unseen.elements()))
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

