import random


class Minesweeper:
    DIFFICULTIES = ['BEGINNER', 'INTERMEDIATE', 'EXPERT']
    difficulty = ''
    stack = []
    stack_index = []
    num_of_flags = None
    num_of_bombs = None
    x_range = None
    y_range = None
    tiles_remaining = None
    game_over = False
    win = False

    def __init__(self, difficulty):
        try:
            self.difficulty = self.DIFFICULTIES[difficulty-1]
        except IndexError:
            print('Invalid difficulty. Must be between 1 and 3')

        self.fill_stack()



    def fill_stack(self):
        """
        Generates the stack with coordinate lists based on difficulty
        Beginner = 8x8
        Intermediate = 16x16
        Expert = 16x31
        :param difficulty: can be 'Beginner', 'Intermediate', or 'Expert'

        """

        if self.difficulty=='BEGINNER':
            self.x_range = 8
            self.y_range = 8
            self.num_of_bombs = 10
            self.num_of_flags = self.num_of_bombs
            self.tiles_remaining = (self.x_range*self.y_range)

            for i in range(self.x_range):
                for j in range(8):
                    self.stack.append([(i, j), 0, False])
            self.generate_stack_index()

        elif self.difficulty=='INTERMEDIATE':
            self.x_range = 16
            self.y_range = 16
            self.num_of_bombs = 40
            self.num_of_flags = self.num_of_bombs
            self.tiles_remaining = (self.x_range*self.y_range)-self.num_of_bombs

            for i in range(self.x_range):
                for j in range(self.y_range):
                    self.stack.append([(i, j), 0, False])
            self.generate_stack_index()

        elif self.difficulty == 'EXPERT':
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
        #tile_index = self.stack_index.index(tile)
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
                #pass
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


    def check_win(self):
        if self.tiles_remaining == self.num_of_bombs:
            self.game_over = True
            self.win = True


    def print_stack(self):
        for i in self.stack:
            print(i)

    def print_stack_index(self):
        for i in range(len(self.stack_index)):
            print("{0}: {1}").format(i, self.stack_index[i])

    def print_grid(self):
        index = 0
        for i in range(self.x_range):
            line = ""
            for j in range(self.y_range):
                if not self.stack[index][2]:
                    line += "| "
                elif self.stack[index][2] == 'F':
                    line += "|F"
                elif self.stack[index][2] == '?':
                    line += "|?"
                else:
                    line += "|{}".format(self.stack[index][1])
                index += 1
            line += '|'
            print line

    def print_exposed_grid(self):
        index = 0
        for i in range(self.x_range):
            line = ""
            for j in range(self.y_range):
                line += "|{}".format(self.stack[index][1])
                index += 1
            line += '|'
            print line

    def get_difficulty(self):
        return self.difficulty
