from FiveYang.token import Token

class Player:

    _instance = None

    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.type = player
        self.num_throws_left = 9
        self.num_defeated_tokens = 0

        self.num_opponent_throws_left = 9
        self.num_opponent_defeated_tokens = 0

        self.tokens = {"r":[], "p":[], "s":[]}
        self.opponent_tokens = {"r":[], "p":[], "s":[]}

        Player._instance = self

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
    
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
            self.tokens[player_action[1]].append[player]
        else:
            player = self.tokens[player_action[1]]
            player.location = player_action[2]
            

        opponent = None
        if opponent_action[0] == "THROW":
            opponent = Token(opponent_action[1], opponent_action[2], True)
            self.opponent_tokens[opponent_action[1]].append[opponent]
        else:
            opponent = self.opponent_tokens[opponent_action[1]]
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
                tokens_on_tile[token.type].append(token)
        
        if tokens_on_tile["r"]: remove_type.append("s")
        if tokens_on_tile["p"]: remove_type.append("r")
        if tokens_on_tile["s"]: remove_type.append("p")

        for r_type in remove_type:
            for token in tokens_on_tile[r_type]:
                self.removeToken(token)

    # remove a token
    def removeToken(self, token):
        if not token.is_opponent: self.tokens[token.type].remove(token)
        else: self.opponent_tokens[token.type].remove(token)

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

    #return the max row that is legal to throw to
    @property
    def max_throw_row(self):
        return 10 - self.throws_left