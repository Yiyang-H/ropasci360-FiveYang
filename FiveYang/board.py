from math import inf
from FiveYang.token import Token
from random import randrange

class Board:
    
    phase = 0
    '''
    Phase 0: normal mode
    Phase 1: survival mode
    Phase 2: chasing mode
    '''
    weight = ((10000, 1000000, 1000),#0: #dead
            (10000, 1000, 1000000), #1: kill
            (5000,5000,0),  #2: #throw_left
            (990,990,990),   #3: #endangered
            (1,1,1),     #4: #distance
            (5000,0,50000),  #Penalty: can't defeat any
            (1000000,1000000,1000000)) #Penalty: opponent has invincible token

    def __init__(self):
        self.upper_num_throws_left = 9
        self.lower_num_throws_left = 9
        self.upper_has_invincible_token = False
        self.lower_has_invincible_token = False

        self.upper_tokens = {"r":[], "p":[], "s":[]}
        self.lower_tokens = {"r":[], "p":[], "s":[]}

    def update(self, upper_action, lower_action):

        
        # updates upper_tokens_list
        if upper_action[0] == "THROW":
            new_token = Token(upper_action[1], upper_action[2], True)
            self.upper_tokens[new_token.token_type].append(new_token)
            self.upper_num_throws_left -= 1
        else:
            self.find_token_at_location(upper_action[1], True).location = upper_action[2]
    
        # updates lower_tokens_list
        if lower_action[0] == "THROW":
            new_token = Token(lower_action[1], lower_action[2], False)
            self.lower_tokens[new_token.token_type].append(new_token)
            self.lower_num_throws_left -= 1
        else:
            self.find_token_at_location(lower_action[1], False).location = lower_action[2]

        self.battle_on_tile(upper_action[2])
        if upper_action[2] != lower_action[2]:
            self.battle_on_tile(lower_action[2])

    
    # Finds a token at a location belongs to a side
    def find_token_at_location(self, location, is_upper):
        tokens_list = []
        if is_upper:
            tokens_list = self.upper_tokens_list
        else:
            tokens_list = self.lower_tokens_list
        for token in tokens_list:
            if token.location == location:
                return token

    # check all the tokens and battle tokens with same location
    def battle(self):
        locations = []
        battle_location = []

        # Find all locations which have multiple tokens
        for token in self.all_tokens_list:
            if token.location not in locations:
                locations.append(token.location)
            else:
                if token.location not in battle_location:
                    battle_location.append(token.location)
        
        # Battle each of the locations
        for location in battle_location:
            self.battle_on_tile(location)

    def battle_on_tile(self, location):
        tokens_on_tile = []
        types_on_tile = []
        for token in self.all_tokens_list:
            if token.location == location:
                tokens_on_tile.append(token)
                if token.token_type not in types_on_tile:
                    types_on_tile.append(token.token_type)
        
        for token in tokens_on_tile:
            if token.enemy_type in types_on_tile:
                self.remove_token(token)
        
    def remove_token(self, token):
        if token.is_upper:
            self.upper_tokens[token.token_type].remove(token)
        else:
            self.lower_tokens[token.token_type].remove(token)

    def terminal_state(self):
        if not self.upper_has_invincible_token: self.has_invincible_token(True)
        if not self.lower_has_invincible_token: self.has_invincible_token(False)

        if self.upper_has_invincible_token and self.lower_has_invincible_token: return "draw"
        elif self.upper_has_invincible_token and len(self.lower_tokens_list) <= 1: return "upper"
        elif self.lower_has_invincible_token and len(self.upper_tokens_list) <= 1: return "lower"

        return None
        
    def has_invincible_token(self, is_upper):
        if is_upper:
            if self.upper_has_invincible_token: return True

            if self.lower_num_throws_left != 0:
                return False
            self.upper_has_invincible_token = self.has_undefeatable_token(is_upper)
            return self.upper_has_invincible_token
        else:
            if self.lower_has_invincible_token: return True

            if self.upper_num_throws_left != 0:
                return False
            self.lower_has_invincible_token = self.has_undefeatable_token(is_upper)
            return self.lower_has_invincible_token



    def has_undefeatable_token(self, is_upper):
        for token in self.ally_tokens_list(is_upper):
            if not self.opponent_tokens(is_upper)[token.enemy_type]:
                return True
        return False

    def eval(self, is_upper):
        terminal = self.terminal_state()
        if terminal:
            if is_upper:
                if terminal == "upper": return 100000000
                elif terminal == "lower": return -100000000
            else:
                if terminal == "lower": return 100000000
                elif terminal == "upper": return -100000000
            return 0
        # weights = (5000, 990, 0, 10000, 0, 14000, 1, -5000, -990, -0, -10000, -0, -14000)

        total = 0
        
        # Feature 1: Difference in dead
        total += self.f4(is_upper) * Board.weight[1][Board.phase] #kill
        total -= self.f4(not is_upper) * Board.weight[0][Board.phase] #dead

        # Feature 2: Difference in throws
        total += (self.f1(is_upper) - self.f1(not is_upper)) * Board.weight[2][Board.phase]

        # Feature 3: Diffenece in endangered tokens
        total += (self.f2(is_upper) - self.f2(not is_upper)) * Board.weight[3][Board.phase]

        # Feature 4: Distance feature (difference?)
        total += (self.f7(is_upper) - self.f2(not is_upper)) * Board.weight[4][Board.phase]

        # Penalty 1: Can't defeat any
        if self.f8(is_upper):
            total -= Board.weight[5][Board.phase]

        # Penalty 2: Opponent has invincible
        if self.has_invincible_token(not is_upper):
            total -= Board.weight[6][Board.phase]

        return total

    # Number of throws left
    def f1(self, is_upper):
        if is_upper:
            return self.upper_num_throws_left
        else:
            return self.lower_num_throws_left

    # Number of oppenent tokens in ally throw zone
    def f2(self, is_upper):
        number = len(self.endangered_tokens(is_upper))
        if number > 0:
            number -= 1
        return number

    def endangered_tokens(self, is_upper):
        endangered_tokens = []
        # check if any throws left
        if is_upper:
            if self.upper_num_throws_left == 0:
                return endangered_tokens
        else:
            if self.lower_num_throws_left == 0:
                return endangered_tokens


        for token in self.opponent_tokens_list(is_upper):
            if self.throwable_location(is_upper, token.location) and not self.is_token_safe(token):
                endangered_tokens.append(token)
        
        return endangered_tokens

    def eatable_tokens(self, is_upper):
        eaten_list = []
        
        for token in self.ally_tokens_list(is_upper):
            valid_moves = self.valid_moves(token)
            for enemy_token in self.opponent_tokens(is_upper)[token.beat_type]:
                if enemy_token.location in valid_moves and enemy_token not in eaten_list and not self.is_token_safe(enemy_token):
                    eaten_list.append(enemy_token)

        return eaten_list

    def f3(self, is_upper):
        return len(self.eatable_tokens(is_upper))

    def f4(self, is_upper):
        if is_upper:
            return (9 - self.lower_num_throws_left) - len(self.lower_tokens_list)
        else:
            return (9 - self.upper_num_throws_left) - len(self.upper_tokens_list)

    def f5(self, is_upper, ):
        total = 0
        if is_upper:
            for token in self.upper_tokens_list:
                total += token.location[0]
        else:
            for token in self.lower_tokens_list:
                total -= token.location[0]

        return total

    def f6(self, is_upper):
        result = 0
        if is_upper:
            for tokens_list in self.upper_tokens:
                if len(tokens_list) > 0: result += 1
            result += self.upper_num_throws_left
        else:
            for tokens_list in self.lower_tokens:
                if len(tokens_list) > 0: result += 1
            result += self.lower_num_throws_left
        if result < 3: return -10
        return 0

    def f7(self, is_upper):
        result = 0
        for token in self.ally_tokens_list(is_upper):
            # increse result for each token I can beat, closer the greater
            opponent_attract = 0
            for opponent in self.opponent_tokens(is_upper)[token.beat_type]:
                opponent_attract += (10 - Board.hex_distance(token.location,opponent.location)) ** 2
            
            opponent_repel = 0
            # decrease result for each token who can beat me if I am not safe
            for opponent in self.opponent_tokens(is_upper)[token.enemy_type]:
                opponent_repel -= (10 - Board.hex_distance(token.location,opponent.location)) ** 2
            if self.is_token_safe(token):
                opponent_repel = 0

            player_attract = 0
            for player in self.ally_tokens(is_upper)[token.beat_type]:
                player_attract += (10 - Board.hex_distance(token.location,player.location)) ** 2
            # attract to ally with beat type


            player_repel = -100
            for player in self.ally_tokens(is_upper)[token.token_type]:
                player_repel += (10 - Board.hex_distance(token.location,player.location)) ** 2
            # repel ally with same type
            result += (opponent_attract*2 + opponent_repel + player_attract*0.1 + player_repel*0.2)

        return result

    # penalty if no opponet I can defeat
    def f8(self, is_upper):
        for token in self.ally_tokens_list(is_upper):
            if self.opponent_tokens(is_upper)[token.beat_type]:
                return False
        return True
    
    # a token is safe if it is stacked with an enemy of same type
    def is_token_safe(self, token):
        for opponent in self.opponent_tokens(token.is_upper)[token.token_type]:
            if opponent.location == token.location:
                return True
        return False

    def skip(self, token):
        valid_moves = self.valid_moves(token)
        for opponent_token in self.opponent_tokens(token.is_upper)[token.beat_type]:
            if opponent_token.location in valid_moves:
                return True
        return False

    '''
    When do we need to put throw actions in successor?
    1. When we have no token on board
    2. When there are enemy in our throw zone
    3. (optional) When there is less than x amount of throws performed in turn y
    
    How many throw actions need to put into successor?
    1. The current location of the enemy token and its neigbours
    (branching factor <=7n)
    2. (optional) Throw the futher token in ally throw zone
    (not minmax)
    '''
    def successor(self, is_upper):
        '''
        move: ("ACTION", (r0,q0), (r1,q1))
        '''
        successors = []
        
        # Put all valid moves for tokens on board into the list
        for token in self.ally_tokens_list(is_upper):
            if not self.is_useful(token): continue
            valid_moves = self.valid_moves(token)
            for valid_move in valid_moves:
                # Need not to specify the action type since its not checked in update method
                action = ("", token.location, valid_move)
                if action not in successors:
                    successors.append(action)

        if not successors:
            for token in self.ally_tokens_list(is_upper):
                if self.is_useful(token): continue
                valid_moves = self.valid_moves(token)
                for valid_move in valid_moves:
                    # Need not to specify the action type since its not checked in update method
                    action = ("", token.location, valid_move)
                    if action not in successors:
                        successors.append(action)
        
        # Put all THROW actions into successors
        # find all opponent tokens in our throw zone
        # find the neighbours of those tokens
        if (is_upper and self.upper_num_throws_left != 0) or (not is_upper and self.lower_num_throws_left != 0):
            # not self.endangered
            for token in self.endangered_tokens(is_upper):
                action = ("THROW", token.enemy_type, token.location)
                if action not in successors:
                    successors.append(action)
                

        # Throw to some specific location on board
        locations = [(4,-2),(3,-2),(2,-1),(1,-1),(0,0),(-1,0),(-2,1),(-3,1),(-4,2)]
        if is_upper:
            locations.reverse()
            for location in locations:
                if self.throwable_location(is_upper, location):
                    for token_type in ["r", "p", "s"]:
                        action = (("THROW", token_type, location))
                        if action not in successors:
                            successors.append(action)
                    break
        else:
            for location in locations:
                if self.throwable_location(is_upper, location):
                    for token_type in ["r", "p", "s"]:
                        action = (("THROW", token_type, location))
                        if action not in successors:
                            successors.append(action)
                    break
        
        return successors
    
    def is_useful(self, token):
        if self.opponent_tokens(token.is_upper)[token.beat_type] or self.opponent_tokens(token.is_upper)[token.enemy_type]: return True
        # TODO
        # also check if this token is too far away from rest of the opponent tokens
        
        return False

    # can ally throw to a location
    def throwable_location(self, is_upper, location):
        if is_upper:
            if self.upper_num_throws_left == 0:
                return False
            row = 4 - (9-self.upper_num_throws_left)
            return location[0] >= row
        else:
            if self.lower_num_throws_left == 0:
                return False
            row = -4 + (9-self.lower_num_throws_left)
            return location[0] <= row

    # simply find all possible moves by a token
    def valid_moves(self, token):
        neighbours = Board.find_neighbours(token.location)
        far_neighbours = []
        current_tokens_list = None
        if token.is_upper:
            current_tokens_list = self.upper_tokens_list
        else:
            current_tokens_list = self.lower_tokens_list
        
        for tok in current_tokens_list:
            if tok.location in neighbours:
                far_neighbours += Board.find_neighbours(tok.location)
        for location in far_neighbours:
            if location not in neighbours and location != token.location:
                neighbours.append(location)
        neighbours.reverse()
        return neighbours
    
    # finds all the neighbours on board of the given location
    @staticmethod
    def find_neighbours(location):
        r = location[0]
        q = location[1]
        neighbours = [(r,q-1),(r,q+1),(r-1,q),(r+1,q),(r-1,q+1),(r+1,q-1)]
        valid_neighbours = []
        for r, q in neighbours:
            if abs(r) <= 4 and abs(q) <= 4 and abs(r+q) <= 4: 
                valid_neighbours.append((r,q))
        
        return valid_neighbours

    @property
    def upper_tokens_list(self):
        return self.upper_tokens["r"] + self.upper_tokens["p"] + self.upper_tokens["s"]
    
    @property
    def lower_tokens_list(self):
        return self.lower_tokens["r"] + self.lower_tokens["p"] + self.lower_tokens["s"]

    @property
    def all_tokens_list(self):
        return self.upper_tokens_list + self.lower_tokens_list

    def ally_tokens_list(self, is_upper):
        if is_upper:
            return self.upper_tokens_list
        else:
            return self.lower_tokens_list
    
    def opponent_tokens_list(self, is_upper):
        if is_upper:
            return self.lower_tokens_list
        else:
            return self.upper_tokens_list

    def ally_tokens(self, is_upper):
        if is_upper:
            return self.upper_tokens
        return self.lower_tokens

    def opponent_tokens(self, is_upper):
        if is_upper:
            return self.lower_tokens
        return self.upper_tokens

    # This function is adapted from hex distance in axial coordinates from
    # https://www.redblobgames.com/grids/hexagons/ 
    @staticmethod
    def hex_distance(a,b):
        return ((abs(a[0] - b[0]) 
            + (abs(a[0] + a[1] - b[0] - b[1]))
            + (abs(a[1] - b[1]))) / 2 )