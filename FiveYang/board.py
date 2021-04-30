from FiveYang.token import Token

class Board:
    weights = (1,1,1,1,1,0,0,0,0,-1,-1,-1,-1)

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
        total = 0
        
        # Feature A1: #ally throws
        total += self.f1(is_upper) * self.weights[0]

        # Feature A2: #opponent tokens in ally throw zone
        total += self.f2(is_upper) * self.weights[1]

        # Feature A3:
        total += self.f3(is_upper) * self.weights[2]

        # Feature A4:
        total += self.f4(is_upper) * self.weights[3]

        # Feature A5:
        total += self.f5(is_upper) * self.weights[4]

        # Feature E1:
        total += self.f1(not is_upper) * self.weights[9]

        # Feature E2:
        total += self.f2(not is_upper) * self.weights[10]

        # Feature E3:
        total += self.f3(not is_upper) * self.weights[11]

        # Feature E4:
        total += self.f4(not is_upper) * self.weights[12]

        # Feature E5:
        total += self.f5(not is_upper) * self.weights[13]

        return total

    # Number of throws left
    def f1(self, is_upper):
        if is_upper:
            return self.upper_num_throws_left
        else:
            return self.lower_num_throws_left

    # Number of oppenent tokens in ally throw zone
    def f2(self, is_upper):
        number = 0
        row = 0
        if is_upper:
            row = 4-(9-self.upper_num_throws_left)
        else:
            row = 4-(9-self.lower_num_throws_left)

        if is_upper:
            for token in self.lower_tokens_list:
                if token.location[0] >= row:
                    number += 1
        else:
            for token in self.upper_tokens_list:
                if token.location[0] <= row * -1:
                    number += 1
        return number

    def f3(self, is_upper):
        eaten_list = []
        ally_tokens_list = None
        enemy_tokens_list = None
        if is_upper:
            ally_tokens_list = self.upper_tokens_list
            enemy_tokens = self.lower_tokens
        else:
            ally_tokens_list = self.lower_tokens_list
            enemy_tokens = self.upper_tokens
        
        for token in ally_tokens_list:
            valid_moves = self.valid_moves(token)
            for enemy_token in enemy_tokens[token.beat_type]:
                if enemy_token.location in valid_moves and enemy_token not in eaten_list:
                    eaten_list.append(enemy_token)

        return len(eaten_list)

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

    # simply find all possible moves by a token
    def valid_moves(self, token):
        neighbours = Board.find_neighbours(token.location)
        far_neighbours = []
        current_tokens_list = None
        if token.is_upper:
            current_tokens_list = self.upper_tokens_list
        else:
            current_tokens_list = self.lower_tokens_list
        
        for token in current_tokens_list:
            if token.location in neighbours:
                far_neighbours += Board.find_neighbours(token.location)
        for location in farNeighbours:
            if location not in neighbours:
                neighbours.append(location)

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
        return upper_tokens["r"] + upper_tokens["p"] + upper_tokens["s"]
    
    @property
    def lower_tokens_list(self):
        return lower_tokens["r"] + lower_tokens["p"] + lower_tokens["s"]

    @property
    def all_tokens_list(self):
        return upper_tokens_list + lower_tokens_list