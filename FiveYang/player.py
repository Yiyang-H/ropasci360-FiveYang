from FiveYang.token import Token
from FiveYang.board import Board
from copy import deepcopy
from math import inf

class Player:

    _instance = None
    upper_start_game = [("THROW", "p", (4, -2)), ("THROW", "r", (3, -2)), ("THROW", "s", (3, -1)), ("SWING",(4,-2),(2,-1)), ("SWING",(3,-2),(1,0))]
    lower_start_game = [("THROW", "p", (-4, 2)), ("THROW", "r", (-3, 2)), ("THROW", "s", (-3, 1)), ("SWING",(-4,2),(-2,1)), ("SWING",(-3,2),(-1,0))]

    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.is_upper = player == "upper"
        self.board = Board()
        self.next_move = None
        self.turn = 0

        #TODO delete this?
        Player._instance = self

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        self.turn += 1
        #  check board to see if apply start game logic or takedown logic
        if self.turn <= 5:
            if self.is_upper:
                return Player.upper_start_game[self.turn-1]
            else:
                return Player.lower_start_game[self.turn-1]

        
        if self.take_down(): 
            return self.take_down()

            
        # put your code here
        self.max_value(deepcopy(self.board), -inf, inf)
        return self.fix_action(self.next_move)
    
    # If we can take down the enemy
    def take_down(self):
        # check all our tokens are safe
        if self.board.f3(not self.is_upper) != 0:
            return None
        if self.board.f3(self.is_upper) == 0:
            return None
        
        enemy_tokens = None
        if self.is_upper:
            enemy_tokens = self.board.lower_tokens
        else:
            enemy_tokens = self.board.upper_tokens
        for token in self.board.ally_tokens_list(self.is_upper):
            valid_moves = self.board.valid_moves(token)
            for enemy_token in enemy_tokens[token.beat_type]:
                if enemy_token.location in valid_moves:
                    action = ("", token.location, enemy_token.location)
                    return self.fix_action(action)
    
    def fix_action(self, action):
        if action[0] == "THROW":
            return action
        else:
            if Player.hex_distance(action[1],action[2]) == 1:
                return ("SLIDE", action[1], action[2])
            else:
                return ("SWING", action[1], action[2])

    
    def update(self, opponent_action, player_action, board = None):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        if board == None:
            board = self.board
        if self.is_upper:
            board.update(player_action, opponent_action)
        else:
            board.update(opponent_action, player_action)

    # A function which perform a search algorithm and returns information  
    # regarding the next move
    def max_value(self, board, alpha, beta, turn_count = 2, first_round = True):
        for action in board.successor(self.is_upper):
            min_val = self.min_value(board, alpha, beta, turn_count, action)
            if first_round and min_val > alpha:
                self.next_move = action
            alpha = max(alpha, min_val)
            

            if alpha >= beta:
                return beta
        return alpha

    def min_value(self, board, alpha, beta, turn_count, player_action):
        turn_count -= 1

        for action in board.successor(not self.is_upper):
            # update the borad

            # print(board.upper_tokens_list)
            # print(board.lower_tokens_list)
            # print(board.successor(not self.is_upper))
            # print(player_action, action)
            new_board = deepcopy(board)
            self.update(action, player_action, new_board)
            # print(board.upper_tokens_list)
            # print(board.lower_tokens_list)
            # chech finished?
            if turn_count == 0:
                return new_board.eval(self.is_upper)
            
            beta = min(beta, self.max_value(new_board, alpha, beta, turn_count, first_round = False))
            if beta <= alpha:
                return alpha
        return beta
    
    @property
    def tokens_dict(self):
        dic = {}
        for token in self.tokens_list:
            if token.location not in dic:
                dic[token.location] = token
        return dic

    # returns a dictionary {location: token}
    @property
    def opponent_tokens_dict(self):
        dic = {}
        for token in self.opponent_tokens_list:
            if token.location not in dic:
                dic[token.location] = token
        return dic

    #return the max row that is legal to throw to
    @property
    def max_throw_row(self):
        return 10 - self.throws_left

    @staticmethod
    def throw_action(token_type, destination):
        return ("THROW", token_type, destination)

    @staticmethod
    def move_action(action_type, origin, destination):
        return (action_type, origin, destination)

    @staticmethod
    def hex_distance(a,b):
        return ((abs(a[0] - b[0]) 
            + (abs(a[0] + a[1] - b[0] - b[1]))
            + (abs(a[1] - b[1]))) / 2 )