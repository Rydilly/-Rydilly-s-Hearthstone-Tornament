Here's a proofread version — fixed spelling, punctuation, and a few grammar slips, but kept your phrasing, structure, and voice intact:

A simplified version of Hearthstone to learn about programmed decision making with imperfect data.
I started with only minions that didn't have any effects and made a few models that followed heuristics, and implementing a few card effects like doom_sayer.
I later tried beating my best flat heuristic bot (doom bot) and struggled for a while.

My first attempt was lethal bot and it got crushed. It used more basic heuristics but was able to spot same-turn lethals unlike any other bot.
Next I refactored the game because it used a ton of deep copies of gamestates for simplicity that really slowed things down with the next model I will talk about.

I then made sample_bot_v2 using a Monte Carlo alg. The MCTS worked by evaluating the board at its current state with a predetermined heuristic for how favorable the board state was. It also used lethal bot before its MCTS.
It also had a bare bones calculation after a card is played by the opponent to predict the likelihood of any card in the opponent's hand.
With this information it made 3 likely branches from all of its legal moves, where in each branch it took the role as its opponent with the predicted hand, using the same alg to decide what is the likely best move the opponent can make.
The best move from that hand would be calculated at a depth of 1, then I allowed the main state to counter that move to get a final score based on the chain.
It failed miserably.

My next approach, sampling_bot_v3, had the same approach as sample_v2 using MCTS, except the evaluation used an array of vectors that were trained overnight with self play.
The cycle followed: play itself for an hour, adjust the vector constants based on results in the games played, check the new constants on a sample of games it didn't have access to while adjusting the constants, and calc the logloss from the sample.
After overnight training my model was close to even with doom, maybe at a small disadvantage.
It wasn't until I added an end turn to my MCTS that the tides changed. The issue with my prior models is that they were having a hard time seeing the impact of playing a board that could get wiped from a doomsayer played on the turn after.
From this one change, still applying the self-learned heuristics from the shallower search sample, it began crushing doom with nearly an 80% wr over 50 games.
Meaning the actual winrate is somewhere between 69%–91% with a confidence of 95%.


I'm now working on adding spells and getting my game to a near-replica state of my favorite deck to assess a mirror matchup.
My end goal is to make a Hearthstone coach similar to the coach chess.com has. Something that can look at a player's game and say "right here was a blunder, you were winning but didn't respect the opponent having this," etc.
A big motivator for this is because in some matchups I've played myself I've felt helpless, and I'm curious if there is counterplay, or if even with the randomness of the game some matchups are truly unwinnable when the opponent doesn't blunder.
