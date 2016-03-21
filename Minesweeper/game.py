from Minesweeper import Minesweeper

print("MINESWEEP")
difficulty = int(input("Please select a difficulty(1-3): "))


minesweeper = Minesweeper(difficulty)
print(minesweeper.num_of_flags)
minesweeper.print_grid()

tile = int(input("Choose a tile: "))
minesweeper.add_bombs(tile)
minesweeper.flip_tile(tile)

while not minesweeper.game_over:
    print(minesweeper.num_of_flags)
    minesweeper.print_grid()
    tile = int(input("Choose a tile: "))
    minesweeper.flip_tile(tile)


if minesweeper.win:
    print("YOU Win!")
    minesweeper.print_exposed_grid()
else:
    print("You lose!")
    minesweeper.print_exposed_grid()