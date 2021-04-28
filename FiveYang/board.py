from FiveYang.token import Token

class Board:
    def __init__(self):
        self.upper_num_throws_left = 9
        self.lower_num_throws_left = 9

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
    def find_token_at_location(self, loation, is_upper):
        tokens_list = []
        if is_upper:
            tokens_list = self.upper_tokens_list
        else:
            tokens_list = self.lower_tokens_list
        for token in tokens_list:
            if token.location == location:
                return token
        ### TODO This line should not be reached, just in case if reached, print error message
        # remove later
        print("="*60,"Something is wrong at find_token_at_location!","="*60,sep="\n")

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
                if token.type not in types_on_tile:
                    types_on_tile.append(token.type)
        
        for token in tokens_on_tile:
            if token.enemy_type in types_on_tile:
                #TODO remove this token
                self.remove_token(token)
        
    def remove_token(self, token):
        if token.is_upper:
            self.upper_tokens[tokens.token_type].remove(token)
        else:
            self.lower_tokens[tokens.token_type].remove(token)

    def eval(self, is_upper):
        pass
    
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
        pass

    @property
    def upper_tokens_list(self):
        return upper_tokens["r"] + upper_tokens["p"] + upper_tokens["s"]
    
    @property
    def lower_tokens_list(self):
        return lower_tokens["r"] + lower_tokens["p"] + lower_tokens["s"]

    @property
    def all_tokens_list(self):
        return upper_tokens_list + lower_tokens_list