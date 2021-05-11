'''
[1400, 1000, 500, 251, 99, 0]
features
+(A)
    1.2 #throws 0-9
    2.4 #opponent_tokens in player throw zone 0-9 
    3.3 #opponent_tokens eatable by player slide / swing actions 0-9
    4.1 #defeated oppenent tokens 0-9
    5.5 Player: sum of (row_weight * current row of each token)
    6.0 diversity protection 0 or 10
    7. distance to nearest meat 0-81


~(N)
    1. Player: sum of (row_weight * current row of each token)
    2. Opponent: sum of (row_weight * current row of each token)
    3. ? #tokens on board
    4. ? #opponent tokens on board

-(E)
    
    1. #opponent_throws
    2. #tokens in opponent throw zone
    3. #tokens eatable by opponent slide / swing actions
    4. #defeated tokens
    5. Opponent: sum of (row_weight * current row of each token)
'''

'''
Modification:
//1. Start game database (ok)
2. Reduce branching factor:
    //1. throw action to current enemy location
    2. Optionally remove all tokens' valid_moves

/3. Taking down enemy logic (to reduce time to run minmaax)
    1. if all our tokens are safe from slide and swing
    2. if some opponent tokens can be take down by slide or swing
    3. 

!4. If both side are fully within their portion of the board, apply different logic
optional 5. Search depth depends on time consumed
/6. check repeated states
7. some tokens will not move this turn
    1. if we are "r" and opponent has no "s" or "p"
    2. if there are tokens other than "r"
    3. if our "r" not in opponent throw zone
8. some tokens will not move this turn
    1. if 1 of our token is more than 4 tiles away from nearest opponent token
    2. if we have more than 1 token alive
    3. if our "r" not in opponent throw zone
//9. protect token diversity logic
    1. if throws_left + #current alive token types < 3, eval -100
    2. Maybe eval -50 for more than 3 tokens of same type exist on board
10. if chased by opponent logic, stand on opponent of same type
11. if two tokens in threat logic, and another opponent token in our throw zone, throw on that token
12. different weight for each 40 turns
13. Throw check to break loop every 20 turns?

### IMPORTANT
    For different logic, check that the action won't cause repeated state

1. If I can eat without ally being eaten, eat enemy
2. If 3 enemy in our throw zone and all our ally safe, throw 1
3. 



'''