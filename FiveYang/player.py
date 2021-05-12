from FiveYang.token import Token
from FiveYang.board import Board
from copy import deepcopy
from math import inf
from random import randint

class Player:

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
        self.history = {}
        self.num_node_visited = 0
        '''
        player_state:[(opponent_state, count)]
        tokens_list: count
        '''


    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        self.turn += 1

        if self.is_upper:
            if self.board.lower_has_invincible_token:
                Board.phase = 1
            if self.board.upper_has_invincible_token:
                Board.phase = 2
        else:
            if self.board.upper_has_invincible_token:
                Board.phase = 1
            if self.board.lower_has_invincible_token:
                Board.phase = 2
        self.next_move = None
        #  check board to see if apply start game logic or takedown logic
        if self.turn <= 5:
            if self.is_upper:
                return Player.upper_start_game[self.turn-1]
            else:
                return Player.lower_start_game[self.turn-1]

        ally_tokens_in_danger = self.board.eatable_tokens(not self.is_upper)
        opponent_tokens_in_danger = self.board.eatable_tokens(self.is_upper)

        logic = self.identify_logic(ally_tokens_in_danger, opponent_tokens_in_danger)
        if logic == "attack":
            self.next_move = self.take_down()
        elif logic == "throw":
            self.next_move = self.throw_logic()
        elif logic == "hide":
            self.next_move = self.hide_logic(ally_tokens_in_danger)
        elif logic == "run":
            self.next_move = self.run_logic(ally_tokens_in_danger)
        elif logic == "trade":
            self.next_move = self.trade_logic(ally_tokens_in_danger, opponent_tokens_in_danger)
            
        # put your code here

        if not self.next_move:
            if len(self.board.all_tokens_list) < 5 and self.num_node_visited < 200000:
                self.max_value(deepcopy(self.board), -inf, inf,2)
            else:
                self.max_value(deepcopy(self.board), -inf, inf,1)
        return self.fix_action(self.next_move)

    # Identify if we can apply some specific logic to the current board
    def identify_logic(self, ally_tokens_in_danger, opponent_tokens_in_danger):
        
        # attack logic: when I can defeat opponent token but opponent cannot defeat mine
        if len(ally_tokens_in_danger) == 0 and len(opponent_tokens_in_danger) > 0:
            return "attack"

        throwable_opponent_tokens = self.board.endangered_tokens(self.is_upper)
        # throw logic: when multiple opponent tokens in my throw zone, and all my tokens are safe
        if len(ally_tokens_in_danger) == 0 and len(throwable_opponent_tokens) >= 3 and self.turn >= 0:
            return "throw"
        # defend logic: when ally_token is in danger, and there is a same type opponent token beside
        if len(ally_tokens_in_danger) == 1 and self.has_same_type(ally_tokens_in_danger):
            return "hide"

        if len(ally_tokens_in_danger) == 1 and self.token_at_corner(ally_tokens_in_danger[0]):
            return "run"

        # trade logic: aggressive trading strategy, 
        #              If my move result one opponent token defeated, take that move
        if len(opponent_tokens_in_danger) - len(ally_tokens_in_danger) > 0:
            return "trade"

    def token_at_corner(self, token):
        corner = [(4,-4),(4,0),(0,4),(-4,4),(-4,0),(0,-4)]
        return token.location in corner
        


    def has_same_type(self, ally_tokens_in_danger):
        for ally in ally_tokens_in_danger:
            valid_moves = self.board.valid_moves(ally)
            for opponent in self.board.opponent_tokens(self.is_upper)[ally.token_type]:
                if opponent.location in valid_moves:
                    return True
        return False

    def hide_logic(self, ally_tokens_in_danger):
        for ally in ally_tokens_in_danger:
            valid_moves = self.board.valid_moves(ally)
            for opponent in self.board.opponent_tokens(self.is_upper)[ally.token_type]:
                if opponent.location in valid_moves:
                    action = ("", ally.location, opponent.location)
                    if self.check_repeated(action):
                        continue
                    return action
    
    def run_logic(self, ally_tokens_in_danger):
        if len(ally_tokens_in_danger) == 1:
            token = ally_tokens_in_danger[0]
            valid_moves = self.board.valid_moves(token)
            opponent_locations = []
            for opponent_token in self.board.opponent_tokens(token.is_upper)[token.enemy_type]:
                if opponent_token.location not in opponent_locations:
                    opponent_locations.append(opponent_token.location)
            
            for valid_move in valid_moves:
                if valid_move not in opponent_locations:
                    action = ("", token.location, valid_move)
                    if self.check_repeated(action):
                        continue
                    return action
        return None


    # When called, meaning we can take down some enemy without sacrifice any ally token
    def take_down(self):
        for token in self.board.ally_tokens_list(self.is_upper):
            valid_moves = self.board.valid_moves(token)
            for enemy_token in self.board.opponent_tokens(self.is_upper)[token.beat_type]:
                if enemy_token.location in valid_moves:
                    action = ("", token.location, enemy_token.location)
                    # Check if current action will cause repeated state
                    if self.check_repeated(action):
                        continue
                    return action
        return None
    
    # When called, meaning we have at least 2/3 chance of defeating one of the enemy token at a cost of throw
    def throw_logic(self):
        throwable_opponent_tokens = self.board.endangered_tokens(self.is_upper)
        # pick one of those opponent tokens
        # pick a random one?
        # throw one which can increse our types?
        # throw the furthest one?
        
        for opponent_token in throwable_opponent_tokens:
            if not self.board.ally_tokens(self.is_upper)[opponent_token.enemy_type]:
                action = ("THROW", opponent_token.enemy_type, opponent_token.location)
                return action
        if throwable_opponent_tokens:
            furthest_opponent_token = throwable_opponent_tokens[0]
            for opponent_token in throwable_opponent_tokens:
                if self.is_upper:
                    if opponent_token.location[0] < furthest_opponent_token.location[0]:
                        furthest_opponent_token = opponent_token
                else:
                    if opponent_token.location[0] > furthest_opponent_token.location[0]:
                        furthest_opponent_token = opponent_token
            action = ("THROW", furthest_opponent_token.enemy_type, furthest_opponent_token.location)
            return action



    # When called, meaning some ally is at risk but at the same time we can take enemy token down as well
    def trade_logic(self, ally_tokens_in_danger, opponent_tokens_in_danger):

        # prioritise in danger ally token
        for token in ally_tokens_in_danger:
            valid_moves = self.board.valid_moves(token)
            for opponent_token in opponent_tokens_in_danger:
                if opponent_token.location in valid_moves and opponent_token.token_type == token.beat_type:
                    action = ("", token.location, opponent_token.location)
                    if self.check_repeated(action):
                        continue
                    return action

        # take down the least opponent type token
        # (count, token_type)
        token_type_count = []
        for token_type in ["r", "p", "s"]:
            token_type_count.append((len(self.board.opponent_tokens(self.is_upper)[token_type]), token_type))
        token_type_count.sort()

        enemy_type = {"r":"p", "p":"s", "s":"r"}
        for token_type in token_type_count:
            for token in self.board.ally_tokens(self.is_upper)[enemy_type[token_type[1]]]:
                valid_moves = self.board.valid_moves(token)
                for opponent_token in opponent_tokens_in_danger:
                    # if this opponent token can eat our token, skip it
                    if self.board.skip(opponent_token):
                        continue
                    if opponent_token.location in valid_moves:
                        action = ("", token.location, opponent_token.location)
                        if self.check_repeated(action):
                            continue
                        return action

    
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
        for_real = False
        if board == None:
            for_real = True
            board = self.board
            if opponent_action[0] == "THROW" or player_action[0] == "THROW":
                self.history = {}
        if self.is_upper:
            board.update(player_action, opponent_action)
        else:
            board.update(opponent_action, player_action)

        if for_real: self.update_history()

    
    def update_history(self):
        ally = Player.token_to_tuple(self.board.ally_tokens_list(self.is_upper)) # num_ally_throw, num_enemy_throw
        opponent = Player.token_to_tuple(self.board.opponent_tokens_list(self.is_upper))

        if ally not in self.history:
            self.history[ally] = (1, {opponent: 1})
        elif opponent not in self.history[ally][1]:
            self.history[ally][1][opponent] = 1
        else:
            self.history[ally][1][opponent] += 1
            if self.history[ally][1][opponent] > self.history[ally][0]:
                self.history[ally] = (self.history[ally][1][opponent], self.history[ally][1])

    def check_repeated(self, action):
        if action[0] == "THROW":
            return False
        # move the current action, check the new ally state
        new_board = deepcopy(self.board)
        new_board.find_token_at_location(action[1], self.is_upper).location = action[2]
        ally = Player.token_to_tuple(new_board.ally_tokens_list(self.is_upper))
        if ally in self.history and self.history[ally][0] >= 2: 
            return True
        return False

    @staticmethod
    def token_to_tuple(tokens_list):
        result = []
        for token in tokens_list:
            result.append((token.token_type, token.location))
        result.sort()
        return tuple(result)
    

    # A function which perform a search algorithm and returns information  
    # regarding the next move
    def max_value(self, board, alpha, beta, turn_count, first_round = True):
        self.num_node_visited += 1
        if turn_count == 0:
                return board.eval(self.is_upper)
        
        for action in board.successor(self.is_upper):
            if first_round and self.check_repeated(action):
                continue
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


            new_board = deepcopy(board)
            self.update(action, player_action, new_board)
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

    # This function is adapted from hex distance in axial coordinates from
    # https://www.redblobgames.com/grids/hexagons/ 
    @staticmethod
    def hex_distance(a,b):
        return ((abs(a[0] - b[0]) 
            + (abs(a[0] + a[1] - b[0] - b[1]))
            + (abs(a[1] - b[1]))) / 2 )