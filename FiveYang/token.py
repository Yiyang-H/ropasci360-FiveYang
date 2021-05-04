class Token:

    def __init__(self, token_type, location, is_upper):
        self.token_type = token_type # r, p, s
        self.location = location
        self.is_upper = is_upper

    # the type this token can beat
    @property
    def beat_type(self):
        if self.token_type == "r": return "s"
        elif self.token_type == "s": return "p"
        return "r" # we are "p"

    # the type this token will lose
    @property
    def enemy_type(self):
        if self.token_type == "r": return "p"
        elif self.token_type == "s": return "r"
        return "s" # we are "p"

    def __repr__(self):
        return self.token_type + " " + str(self.location)