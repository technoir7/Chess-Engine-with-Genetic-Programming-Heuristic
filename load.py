# Step 1: Reading Chess Games from PGN

# Imagine our PGN file is like a special book of chess games
pgn_file = "chess_games.pgn"

# Let's open the book and read the games one by one
with open(pgn_file, "r") as file:
    # We'll read the contents of the book into a variable called "pgn_content"
    pgn_content = file.read()

# Step 2: Converting PGN to Moves

# Next, let's turn the chess games in our book (pgn_content) into individual games

# Imagine each chess game is like a separate adventure in the book
# We'll split the games based on the special symbol "[Event " that starts each game

# We'll use the "split()" function to do the splitting magic!
# Each game will be stored in our list of chess games
all_chess_games = pgn_content.split("[Event ")[1:]  # We skip the first empty item

# Step 3: One-Hot Encoding - Superhero Transformation!

# Next, let's give our superhero chess moves their superhero powers with one-hot encoding!

# Imagine each superhero chess move gets its own special box with switches
# Each switch can be ON (1) or OFF (0) - just like a light switch at home

# Let's start with an empty list to store our superhero powers for each game
all_one_hot_encodings = []

# Each move will have its own superhero power switches
# We'll loop through all our chess games and their superhero moves

for chess_game in all_chess_games:
    # We'll split the moves of the chess game based on the special symbol " " (space)
    pgn_moves = chess_game.split()

    # Let's create a list to store superhero powers (one-hot encoding) for each move in this game
    one_hot_encodings = []

    for pgn_move in pgn_moves:
        # Implement the logic to convert the move to square numbers and encode it as one-hot
        # Append the one hot encoding to the one_hot_encodings list

    # Now we have all the moves for this game encoded as one-hot encodings
    # Let's add the list of one hot encodings for this game to the list of all games
    all_one_hot_encodings.append(one_hot_encodings)

# Now, the all_one_hot_encodings list contains all the superhero chess moves from multiple games!
# Each game's moves are stored as a list of superhero moves in the order they appeared in the PGN file,
# and each move is encoded as a one-hot representation.

# Ta-da! Now we have all our superhero moves from multiple games with their superhero powers (one-hot encoded)!
print("Superhero Chess Moves from Multiple Games with Superpowers (One-Hot Encoded):")
print(all_one_hot_encodings)
