# Make a game Project 4: MineSweeperApi

## Set-Up Instructions:
1. Update the value of application in app.yaml to the app ID you have registered in the App Engine admin console and would like to use to host your instace of this app.
2. Run the app with the devserver using dev_appserver.py DIR, and ensure it's running by visiting API Explorer - by default locahost:8080/_ah/explorer.
3.(Optional) Generate your client library(ies) with the endpoints tool. Deploy your application

## Game Description:
Minesweeper is a single player puzzle game. The player is presented with a grid, and must find all the hidden mines without detonating any. Numbered tiles are hidden around the mines to indicate how many are nearby. It is up to the player to then deduce the location of the mines. Using 'make_move', inputing online a tile number flips the tile. Including a True in the input allows the user to flap a tile without flipping it. Multiple games can be played at the same time and accessed with the path parameter 'urlsafe_game_key'.

## Files Included:
- api.py: Contains endpoints and game playing logic.
- app.yaml: App configuration.
- cron.yaml: Cronjob configuration.
- main.py: Handler for taskqueue handler.
- models.py: Entity and message definitions including helper methods.
- utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

## Endpoints Included:
- **create_user**
   - Path: 'user'
   - Method: POST
   - Parameters: user_name, email (optional)
   - Returns: Message confirming creation of the User.
   - Description: Creates a new User. user_name provided must be unique. Will
   raise a ConflictException if a User with that user_name already exists.

- **new_game**
  - Path: 'game'
  - Method: POST
  - Parameters: user_name, difficulty
  - Returns: GameForm with initial game state.
  - Description: Creates a new Game. user_name provided must correspond to an
  existing user - will raise a NotFoundException if not. Min must be less than
  max. Also adds a task to a task queue to update the average moves remaining
  for active games.

- **get_game**
     - Path: 'game/{urlsafe_game_key}'
     - Method: GET
     - Parameters: urlsafe_game_key
     - Returns: GameForm with current game state.
     - Description: Returns the current state of a game.

- **make_move**
  - Path: 'game/{urlsafe_game_key}'
  - Method: PUT
  - Parameters: urlsafe_game_key, tile, flag(default=False)
  - Accepts a tile and a Flag boolean. If the flag input is set to false or left blank, the selected tile will be flip. If the flag is set True, the tile with be marked as flagged, without flipping it. If a mine is selected will end game. If all non-mine tiles are flipped, the game ends and the player wins.

- **get_scores**
  - Path: 'scores'
  - Method: GET
  - Parameters: None
  - Returns: ScoreForms.
  - Description: Returns all Scores in the database (unordered).

- **get_user_scores**
     - Path: 'scores/user/{user_name}'
     - Method: GET
     - Parameters: user_name
     - Returns: ScoreForms.
     - Description: Returns all Scores recorded by the provided player (unordered).
     Will raise a NotFoundException if the User does not exist.

## Models Included:
- **User**
  - Stores unique user_name and (optional) email address.

- **Game**
  - Stores unique game states. Associated with User model via KeyProperty.

- **Score**
  - Records completed games. Associated with Users model via KeyProperty.

##Forms Included:
   - **GameForm**
      - Representation of a Game's state (urlsafe_key, tiles_remaining,
      flag_remaining, num_of_bombs, game_over, message, usr_name, stack, stack_index).
   - **NewGameForm**
      - Used to create a new game (user_name, difficulty)
   - **MakeMoveForm**
      - Inbound make move form (tile, flag).
   - **ScoreForm**
      - Representation of a completed game's Score (user_name, date, won flag,
      tiles_remaining).
   - **ScoreForms**
      - Multiple ScoreForm container.
   - **StringMessage**
      - General purpose String container.
