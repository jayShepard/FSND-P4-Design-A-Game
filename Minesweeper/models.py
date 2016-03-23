"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        if self.total_played > 0:
            return float(self.wins)/float(self.total_played)
        else:
            return 0

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        total_played=self.total_played,
                        win_percentage=self.win_percentage)

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.total_played += 1
        self.put()

    def add_loss(self):
        """Add a loss"""
        self.total_played += 1
        self.put()

class Game(ndb.Model):
    """Game object"""

    x_range = ndb.IntegerProperty(required=True)
    stack = ndb.PickleProperty(required=True)
    stack_index = ndb.PickleProperty(required=True)
    difficulty = ndb.IntegerProperty(required=True)
    y_range = ndb.IntegerProperty(required=True)
    num_of_bombs = ndb.IntegerProperty(required=True)
    flags_remaining = ndb.IntegerProperty(required=True)
    tiles_remaining = ndb.IntegerProperty(required=True)
    win = ndb.BooleanProperty(required=True, default=False)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    first_move = ndb.BooleanProperty(required=True, default=True)
    history = ndb.PickleProperty()

    @classmethod
    def new_game(cls, user, difficulty):
        DIFFICULTIES = [1, 2, 3]
        """Creates and returns a new game"""
        if difficulty not in DIFFICULTIES:
            raise ValueError('Invalid difficulty')

        game = Game(user=user,
                    difficulty=difficulty)

        if difficulty==1:
            game.x_range = 8
            game.y_range = 8
            game.num_of_bombs = 10

        elif difficulty==2:
            game.x_range = 16
            game.y_range = 16
            game.num_of_bombs = 40

        elif difficulty == 3:
            game.x_range = 16
            game.y_range = 31
            game.num_of_bombs = 99

        game.flags_remaining = game.num_of_bombs
        game.tiles_remaining = (game.x_range*game.y_range)-game.num_of_bombs
        game.stack = []
        game.stack_index = []
        game.history = []
        for i in range(game.x_range):
            for j in range(game.y_range):
                game.stack.append({'coordinate': (i, j),'value': 0,
                                    'flip': False, 'flag': False})
        for i in range(len(game.stack)):
            game.stack_index.append(game.stack[i]['coordinate'])
        game.put()
        return game

    def to_form(self, message=None):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.tiles_remaining = self.tiles_remaining
        form.flag_remaining = self.flags_remaining
        form.num_of_bombs = self.num_of_bombs
        form.game_over = self.game_over
        form.stack = str(self.stack)
        form.stack_index = str(self.stack_index)
        form.message = message
        form.difficulty = self.difficulty
        return form

    def generate_stack_index(self):
        """indexes the coordinates so their index is searchable"""
        for i in range(len(self.stack)):
            self.stack_index.append(self.stack[i]['coordinate'])

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()

    def add_bombs(self, protected_tile):
        """adds bombs into the stack, making sure not place one on the
        protected_tile
        """
        bomb_list =[]
        count = self.num_of_bombs

        while count > 0:
            index = random.randint(0, len(self.stack)-1)
            if not(self.stack[index]['value'] == 'bomb' or index == protected_tile):
                self.stack[index]['value'] = 'bomb'
                count -= 1
                bomb_list.append(index)
        self.add_bomb_proximities(bomb_list)

    def add_bomb_proximities(self, bomb_list):
        """surrounds bombs with proximity numbers"""
        for bomb in bomb_list:
            nodes = self.find_connecting_indexes(bomb)
            for node in nodes:
                value = self.stack[node]['value']
                if value == 'bomb':
                    continue
                else:
                    self.stack[node]['value'] += 1

    def find_connecting_indexes(self, index):
        """:Returns: a list of all adjacent indexes to a given index"""
        nodes = []
        x = self.stack_index[index][0]
        y = self.stack_index[index][1]

        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if (i == x and j == y):
                    continue
                else:
                    try:
                        ad_index = self.stack_index.index((i,j))
                        nodes.append(ad_index)
                    except:
                        continue
        return nodes

    def flip_tile(self, tile, flag=False):
        #tile_index = self.stack_index.index(tile)

        selected_tile = self.stack[tile]

        if flag == True:
            if self.flags_remaining == 0:
                raise ValueError("No flags left")
            else:
                selected_tile['flag']=True
                self.flags_remaining -= 1

        else:
            if selected_tile['flag'] == True:
                selected_tile['flag'] == False
                self.flags_remaining += 1

            else:
                self.stack[tile]['flip'] = True
                self.tiles_remaining -= 1
                if selected_tile['value'] == 'bomb':
                    self.end_game()
                elif selected_tile['value'] == 0:
                    self.blank_tile_cascade(tile)
                self.check_win()

    def blank_tile_cascade(self, tile):
        """Checks all surrounding nodes for 0 value, and flips them.
        Recursively checks each new empty node.
        """
        nodes = self.find_connecting_indexes(tile)
        for node in nodes:
            if self.stack[node]['value'] != 0:
                self.stack[node]['flip'] = True
                continue
            else:
                if not self.stack[node]['flip']:
                    self.stack[node]['flip'] = True
                    self.tiles_remaining -= 1
                    self.blank_tile_cascade(node)

    def check_win(self):
        if self.tiles_remaining == self.num_of_bombs:
            self.win = True
            self.end_game()

    def end_game(self):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=self.win,
                      tiles_remaining=self.tiles_remaining,
                      difficulty=self.difficulty)
        score.put()

    def add_to_game_history(self, tile, flag=False):
        move = {
        'tile': tile,
        'flag':flag,
        'coordinate': self.stack[tile]['coordinate'],
        'value': self.stack[tile]['value']}
        self.history.append(move)

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    tiles_remaining = ndb.IntegerProperty(required=True)
    difficulty = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         won=self.won,
                         date=str(self.date),
                         tiles_remaining=self.tiles_remaining,
                         difficulty=self.difficulty)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    tiles_remaining = messages.IntegerField(2, required=True)
    flag_remaining = messages.IntegerField(3, required=True)
    num_of_bombs = messages.IntegerField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    message = messages.StringField(6)
    user_name = messages.StringField(7, required=True)
    stack = messages.StringField(8, required=True)
    stack_index = messages.StringField(9, required=True)
    difficulty = messages.IntegerField(10)

class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    difficulty = messages.IntegerField(2, default=1)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    tile = messages.IntegerField(1, required=True)
    flag = messages.BooleanField(2, default=False)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    tiles_remaining = messages.IntegerField(4, required=True)
    difficulty = messages.IntegerField(5,)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_played = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)
