from Basic.token import Token
import random
import time

class Player:

    _instance = None

    def __init__(self, player):
        self.player = player
        self.num_throws_left = 9
        self.num_defeated_tokens = 0

        self.num_opponent_throws_left = 9
        self.num_opponent_defeated_tokens = 0

        self.tokens = {"r":[], "p":[], "s":[]}
        self.opponent_tokens = {"r":[], "p":[], "s":[]}

        Player._instance = self

    def action(self):
        # simulate thinking for 0.5 seconds
        time.sleep(0.5)
        
        # TODO check opponent token in our throw region
        

        # if we do not have a token
        throw = False
        if self.tokens_list:
            # decide what to do
            action = random.randint(0, len(self.tokens_list))
            if self.num_throws_left == 0: action = random.randint(0, len(self.tokens_list)-1)

            if action == len(self.tokens_list): 
                # throw a token
                throw = True
            else:
                # slide a token
                token = self.tokens_list[action]
                valid_moves = self.valid_moves(token.location)
                return ("SLIDE", token.location, valid_moves[random.randint(0, len(valid_moves)-1)])
        
        if not self.tokens_list or throw:
            if not self.opponent_tokens["r"]:
                token_type = "r"
                return Player.throw_action(token_type, self.random_throw_tile())
            elif not self.opponent_tokens["p"]:
                token_type = "p"
                return Player.throw_action(token_type, self.random_throw_tile())
            elif not self.opponent_tokens["s"]:
                token_type = "s"
                return Player.throw_action(token_type, self.random_throw_tile())
            else:
                token_type = self.tokens.keys()[random.randint(0, 2)]
                return Player.throw_action(token_type, self.random_throw_tile())
    
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # perform all move actions
        player = None
        if player_action[0] == "THROW":
            player = Token(player_action[1], player_action[2], False)
            self.tokens[player_action[1]].append(player)
            self.num_throws_left -= 1
        else:
            player = self.tokens_dict[player_action[1]]
            player.location = player_action[2]
            

        opponent = None
        if opponent_action[0] == "THROW":
            opponent = Token(opponent_action[1], opponent_action[2], True)
            self.opponent_tokens[opponent_action[1]].append(opponent)
            self.num_opponent_throws_left -= 1
        else:
            opponent = self.opponent_tokens_dict[opponent_action[1]]
            opponent.location = opponent_action[2]

        # collision handling
        self.battle_on_tile(opponent_action[2])
        if player_action[2] != opponent_action[2]: self.battle_on_tile(player_action[2])

    # remove all tokens that should be killed on a tile
    def battle_on_tile(self, location):
        tokens_on_tile = {"r":[], "p":[], "s":[]}

        remove_type = []

        for token in self.all_tokens_list:
            if token.location == location:
                tokens_on_tile[token.token_type].append(token)
        
        if tokens_on_tile["r"]: remove_type.append("s")
        if tokens_on_tile["p"]: remove_type.append("r")
        if tokens_on_tile["s"]: remove_type.append("p")

        for r_type in remove_type:
            for token in tokens_on_tile[r_type]:
                self.removeToken(token)

    # remove a token
    def removeToken(self, token):
        if not token.is_opponent: self.tokens[token.token_type].remove(token)
        else: self.opponent_tokens[token.token_type].remove(token)

    # return the list of currently alive tokens on our side
    @property
    def tokens_list(self):
        return self.tokens["r"] + self.tokens["p"] + self.tokens["s"]

    # return the list of currently alive tokens on opponent side
    @property
    def opponent_tokens_list(self):
        return self.opponent_tokens["r"] + self.opponent_tokens["p"] + self.opponent_tokens["s"]

    @property
    def all_tokens_list(self):
        return self.tokens_list + self.opponent_tokens_list

    # returns a dictionary {location: token}
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
    def valid_moves(location):
        r,q = location
        neighbours = [(r,q-1),(r,q+1),(r-1,q),(r+1,q),(r-1,q+1),(r+1,q-1)]
        valid_moves = []
        for r,q in neighbours:
            if Player.is_valid_tile(r, q):
                valid_moves.append((r,q))
        
        return valid_moves

    @staticmethod
    def is_valid_tile(r, q):
        if abs(r) <= 4 and abs(q) <= 4 and abs(r+q) <= 4:
            return True
        return False

    def random_throw_tile(self):
        top = 4
        bottom = -4
        if self.player == "upper": bottom = -5 + self.num_throws_left
        else: top = 5 - self.num_throws_left
        
        while True:
            new_tile = (random.randint(bottom, top), random.randint(-4, 4))
            print(new_tile)
            if Player.is_valid_tile(new_tile[0], new_tile[1]):
                return new_tile