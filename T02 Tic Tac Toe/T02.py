import os
import time
import random

# ---

NL = '\n'

# ---

GAMES_TO_PLAY = 10
SLEEP_TIME = 0.1

# ---

players = [
  {
    'Name': 'Bob',
    'Symbol': 'X',
    'Wins': 0
  },
  {
    'Name': 'Alice',
    'Symbol': 'O',
    'Wins': 0
  }
]

# Board stored as 3D char array
board = [[' ' for i in range(3)] for j in range(3)]
winner = None
draws = 0
topBar = ''
bottomBar = ''

# Represents each possible 'line' of three cells that can be used to win the game.
# This is used both by the core game loop and the AIs.
potentialLines = [
  [[0,0], [0,1], [0,2]],
  [[1,0], [1,1], [1,2]],
  [[2,0], [2,1], [2,2]],
  [[0,0], [1,0], [2,0]],
  [[0,1], [1,1], [2,1]],
  [[0,2], [1,2], [2,2]],
  [[0,0], [1,1], [2,2]],
  [[0,2], [1,1], [2,0]]
]

# ---

def printBoard():
  
  # We store the basic building blocks of the board display here
  hLine   = ' -----+-----+----- '
  vLines  = '      |     |      '
  symbols = '   {}  |  {}  |  {}   '
  
  rowTemplate = vLines + NL + symbols + NL + vLines
  
  boardTemplate = \
    rowTemplate + NL + hLine + NL + \
    rowTemplate + NL + hLine + NL + \
    rowTemplate
  
  boardAsText = boardTemplate.format(
    board[0][0], board[0][1], board[0][2],
    board[1][0], board[1][1], board[1][2],
    board[2][0], board[2][1], board[2][2]
  )
  
  # Clear the console before reprinting the board
  os.system('cls')
  print(NL+topBar)
  print(NL+boardAsText)
  print(NL+bottomBar)
    
  # If we're simulating multiple games, display the win tally for each player below  
  if GAMES_TO_PLAY > 1:
    print(
      NL + 'Wins:' + \
      NL + '---+---' + \
      NL + ' ' + players[0]['Symbol'] + ' | ' + players[0]['Name'] + ': ' + str(players[0]['Wins']) + \
      NL + ' ' + players[1]['Symbol'] + ' | ' + players[1]['Name'] + ': ' + str(players[1]['Wins']) + \
      NL + ' . | Draws: '+str(draws)
    )
  
# ---

def resetGame():
  global winner
  global board
  winner = None
  board = [[' ' for i in range(3)] for j in range(3)]

# ---

def isValid(move):
  return board[move['Position'][0]][move['Position'][1]] == ' '

# ---

def executeMove(move):
  global board
  board[move['Position'][0]][move['Position'][1]] = move['Symbol']
  
# ---  

def checkPotentialTriple(symbol, symbolCount, posA, posB, posC):
  # Does the specified [symbol] appear in [symbolCount] of the three specified positions, 
  # with the remaining position(s) being blank?
  
  hasSymbol = 0
  
  boardCells = [
    board[posA[0]][posA[1]], 
    board[posB[0]][posB[1]], 
    board[posC[0]][posC[1]]
  ]
  
  for cellValue in boardCells:
    if cellValue == symbol:
      hasSymbol += 1
    elif cellValue != ' ':
      return False
      
  return hasSymbol == symbolCount 
  
# ---  
  
def isGameOver():
  # Check all potential winning lines. If a player has filled a line, they are the winner.
  global winner
  for player in players:
    for line in potentialLines:
      if checkPotentialTriple(player['Symbol'], 3, line[0], line[1], line[2]):
        winner = player
        return True
  return False
  
# ---

def getValidMove(player, potentialMoves = []):
  # If we've been passed a list of moves to try, iterate over them and pick the first valid move
  for movePos in potentialMoves:
    move = {
      'Position': [movePos[0], movePos[1]],
      'Symbol': player['Symbol']
    }
    if isValid(move):
      return move
      
  # If we haven't been passed any moves to try (or if none of the specified moves are valid),
  # just keep trying random moves until one is valid.  
  while True:
    move = {
      'Position': [random.randint(0,2), random.randint(0,2)],
      'Symbol': player['Symbol']
    }
    if isValid(move):
      return move

   # Important: This assumes that there exists at least one valid move. In other words, don't remove the 
   # turnNum == 9 check in the main loop or this will continue searching for moves indefinitely.
      
# ---

def getP1Move():

  # P1: Pretty good AI. Tries to win, also tries to prevent the other AI from winning.

  # 1/ If we can win this turn, finish the game
  for line in potentialLines:
    if checkPotentialTriple(players[0]['Symbol'], 2, line[0], line[1], line[2]):
      return getValidMove(players[0], line)

  # 2/ If other player is about to win, block them
  for line in potentialLines:
    if checkPotentialTriple(players[1]['Symbol'], 2, line[0], line[1], line[2]):
      return getValidMove(players[0], line)
      
  # 3/ Choose a random valid move
  return getValidMove(players[0])
  
# ---

def getP2Move():

  # P2: Not very good AI. Just picks a random, valid move.

  # # If we can win this turn, finish the game
  # for line in potentialLines:
  #   if checkPotentialTriple(players[1]['Symbol'], 2, line[0], line[1], line[2]):
  #     return getValidMove(players[1], line)
  # 
  # # If other player is about to win, block them
  # for line in potentialLines:
  #   if checkPotentialTriple(players[0]['Symbol'], 2, line[0], line[1], line[2]):
  #     return getValidMove(players[1], line)
      
  # 1/ Choose a random valid move
  return getValidMove(players[1])

# ---

for gameNum in range(1, GAMES_TO_PLAY+1):

  # Display information about the two players, as well as the game number (if move than one game is to be played)
  topBar = 'Tic Tac Toe - {} ({}) vs. {} ({}){}'.format(
    players[0]['Name'], players[0]['Symbol'],
    players[1]['Name'], players[1]['Symbol'],
    (' Game #'+str(gameNum)) if GAMES_TO_PLAY > 1 else '' 
  )

  resetGame()
  
  turnNum = 1
  while winner is None:

    # Switch moves every turn and switch turn order every game
    P1Turn = turnNum % 2 == gameNum % 2

    bottomBar = 'Turn {}, {}''s move...'.format(
      turnNum, players[0]['Name'] if P1Turn else players[1]['Name']
    )

    move = getP1Move() if P1Turn else getP2Move()

    # Each AI should only ever return valid moves, but just in case I've left this check in
    if isValid(move):
      executeMove(move)
    else:
      print('Invalid Move.')
      break
    
    if isGameOver():
      # Display the winner 
      bottomBar = 'Game over! Winner is '+winner['Name']
      winner['Wins'] += 1
      printBoard()
      # Sleep for longer than usual before the next game
      if SLEEP_TIME > 0:   
        time.sleep(SLEEP_TIME*5)
      break
      
    if turnNum == 9:
      # We've reached turn 9 with no winner. Game is declared a draw.
      bottomBar = 'Draw.'
      draws += 1
      printBoard()
      if SLEEP_TIME > 0:   
        time.sleep(SLEEP_TIME*5)
      break
          
    # If the sleep time is zero, we don't bother printing the board each loop (just when the game ends)
    if SLEEP_TIME > 0:   
      printBoard()
      time.sleep(SLEEP_TIME)
    
    turnNum += 1