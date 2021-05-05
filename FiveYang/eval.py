'''
features
+(A)
    1. #throws
    2. #opponent_tokens in player throw zone
    3. #opponent_tokens eatable by player slide / swing actions
    4. #defeated oppenent tokens
    5. Player: sum of (row_weight * current row of each token)
    6. 3 piece gatherings?


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
1. Start game database (ok)
2. Reduce branching factor:
    1. throw action to current enemy location
    2. Optionally remove all tokens' valid_moves

3. Taking down enemy logic (to reduce time to run minmaax)
    1. if all our tokens are safe from slide and swing
    2. if some opponent tokens can be take down by slide or swing
    3. 

4. If both side are fully within their portion of the board, apply different logic
5. Search depth depends on time consumed
6. Avoid rock going left and right
'''