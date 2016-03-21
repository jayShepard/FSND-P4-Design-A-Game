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
    grid_stack =
    num_of_bombs = ndb.IntegerProperty(required=True, default=None)
    x_range = ndb.IntegerProperty(required=True, default=None)
    y_range = ndb.IntegerProperty(required=True, default=None)
    game_over = ndb.BooleanProperty(required=True, default=False)

    user = ndb.KeyProperty(required=True, kind='User')
    won = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user, difficulty):
        """Creates and returns a new game"""

        if max < min:
            raise ValueError('Maximum must be greater than minimum')
        game = Game(user=user,
                    target=random.choice(range(1, max + 1)),
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    game_over=False)
        game.put()
        return game

    def fill_stack(self):
        """
        Generates the stack with coordinate lists based on difficulty
        Beginner = 8x8
        Intermediate = 16x16
        Expert = 16x31
        :param difficulty: can be 'Beginner', 'Intermediate', or 'Expert'

        """
        if self.difficulty==1:
            self.x_range = 8
            self.y_range = 8
            self.num_of_bombs = 10
            self.num_of_flags = self.num_of_bombs
            self.tiles_remaining = (self.x_range*self.y_range)

            for i in range(self.x_range):
                for j in range(8):
                    self.stack.append([(i, j), 0, False])
            self.generate_stack_index()

        elif self.difficulty==2:
            self.x_range = 16
            self.y_range = 16
            self.num_of_bombs = 40
            self.num_of_flags = self.num_of_bombs
            self.tiles_remaining = (self.x_range*self.y_range)-self.num_of_bombs

            for i in range(self.x_range):
                for j in range(self.y_range):
                    self.stack.append([(i, j), 0, False])
            self.generate_stack_index()

        elif self.difficulty == 3:
            self.x_range = 16
            self.y_range = 31
            self.num_of_bombs = 99
            self.num_of_flags = self.num_of_bombs
            self.tiles_remaining = (self.x_range*self.y_range)-self.num_of_bombs

            for i in range(self.x_range):
                for j in range(self.y_range):
                    self.stack.append([(i, j), 0, False])
            self.generate_stack_index()

        else:
            raise ValueError('Invalid difficulty')

    def add_bombs(self, protected_tile):
        bomb_list = []
        count = self.num_of_bombs

        while count > 0:
            index = random.randint(0, len(self.stack)-1)
            if self.stack[index][1] != '#' or index != protected_tile:
                self.stack[index][1] = '#'
                count -= 1
                bomb_list.append(index)
        self.add_bomb_proximities(bomb_list)

    def generate_stack_index(self):
        """indexes the coordinates so their index is searchable"""
        for i in range(len(self.stack)):
            self.stack_index.append(self.stack[i][0])

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
    def add_bomb_proximities(self, mine_list):
        """surrounds bombs with proximity numbers"""

        for mine in mine_list:
            nodes = self.find_connecting_indexes(mine)
            for node in nodes:
                value = self.stack[node][1]
                if value == '#':
                    continue
                else:
                    self.stack[node][1] += 1

    def flip_tile(self, tile, flag=None):

        tile_value = self.stack[tile][1]

        if self.stack[tile][2]:
            if flag == 'F':
                if self.num_of_flags == 0:
                    raise ValueError
                else:
                    self.stack[tile][2] = 'F'
                    self.num_of_flags -= 1

            elif flag == '?':
                self.stack[tile][2] = '?'

        else:
            self.stack[tile][2] = True
            self.tiles_remaining -= 1
            if tile_value == '#':
                self.game_over = True
            elif tile_value == 0:

                self.blank_tile_cascade(tile)
            self.check_win()


    def blank_tile_cascade(self, tile):
        """Checks all surrounding nodes for 0 value, and flips them.
        Recursively checks each new empty node.
        """
        nodes = self.find_connecting_indexes(tile)
        for node in nodes:
            if self.stack[node][1] != 0:
                self.stack[node][2] = True
                continue
            else:
                if not self.stack[node][2]:
                    self.stack[node][2] = True
                    self.tiles_remaining -= 1
                    self.blank_tile_cascade(node)


    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


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
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, default=10)
    attempts = messages.IntegerField(4, default=5)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.IntegerField(1, required=True)


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
