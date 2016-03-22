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


class Game(ndb.Model):
    """Game object"""

    x_range = ndb.IntegerProperty(required=True)
    stack = ndb.PickleProperty(required=True)
    stack_index = ndb.PickleProperty(required=True)
    difficulty = ndb.IntegerProperty(required=True)
    y_range = ndb.IntegerProperty(required=True)
    num_of_bombs = ndb.IntegerProperty(required=True)
    flags_remaining = ndb.IntegerProperty(required=True)
    #num_of_tiles = ndb.IntegerProperty(required=True)
    #tiles_flipped = ndb.IntegerProperty(required=True)
    tiles_remaining = ndb.IntegerProperty(required=True)
    win = ndb.BooleanProperty(required=True, default=False)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    first_move = ndb.BooleanProperty(required=True, default=True)

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
        for i in range(game.x_range):
            for j in range(game.y_range):
                game.stack.append({'coordinate': (i, j),'value': 0,
                                    'flip': False, 'flag': False})
        for i in range(len(game.stack)):
            game.stack_index.append(game.stack[i]['coordinate'])
        game.put()
        return game

    def to_form(self, message):
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
        bomb_list =[]
        count = self.num_of_bombs

        while count > 0:
            index = random.randint(0, len(self.stack)-1)
            if self.stack[index]['value'] != '#' or index != protected_tile:
                self.stack[index]['value'] = '#'
                count -= 1
                bomb_list.append(index)
        #self.add_bomb_proximities(bomb_list)

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    tiles_remaining = messages.IntegerField(2, required=True)
    flag_remaining = messages.IntegerField(3, required=True)
    num_of_bombs = messages.IntegerField(4, required=True)
    game_over = messages.BooleanField(5, required=True)
    message = messages.StringField(6, required=True)
    user_name = messages.StringField(7, required=True)
    stack = messages.StringField(8, required=True)
    stack_index = messages.StringField(9, required=True)

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
    guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
