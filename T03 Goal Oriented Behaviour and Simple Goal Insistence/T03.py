import sys
import os
import time

# ---

goals = {
  'Get enough sleep': 3,
  'Pass exams': 5,
  'Party hard': 4
}

actions = {
  'Go to bed': {
    'Get enough sleep': -2,
    'Pass exams': 1,
    'Party hard': 0
  },
  'Pull all-nighter at the Library': {
    'Get enough sleep': 5,
    'Pass exams': -4,
    'Party hard': 1
  },
  'Study for exams': {
    'Get enough sleep': 0,
    'Pass exams': -2,
    'Party hard': 1
  },
  'Have a few quiet drinks with the lads': {
    'Get enough sleep': 0,
    'Pass exams': 1,
    'Party hard': -2
  },
  'Head to Revs': {
    'Get enough sleep': 5,
    'Pass exams': 1,
    'Party hard': -4
  }
}

# ---

def cls():
  os.system('cls')

# ----

def printGoalValues():
  cls()
  print()
  for goal, value in goals.items():
    print(goal.ljust(20) + '| ' + str(value).rjust(2) + ' | ' + ('#'*value))

# ---

def goalsAchieved():
  for goal, value in goals.items():
    if value > 0:
      return False
  return True

# ---

def goalFailed():
  for goal, value in goals.items():
    if value >= 10:
      return True
  return False
  
# ---

def chooseMostImportantGoal():
  result = None
  for goal, value in goals.items():
    if result == None or (value > goals[result] and value > 0):
      result = goal
  return result

# ---

def getUtility(goal, outcomes):
  algorithms = {
    '1': getUtility1,
    '2': getUtility2,
    '3': getUtility3,
  }
  return algorithms[sys.argv[1]](goal, outcomes)
  
# ---  

def getUtility1(goal, outcomes):
  return -outcomes[goal]

# ---  

def getUtility2(goal, outcomes):
  for outcomeGoal, outcomeChange in outcomes.items():
    if goals[outcomeGoal] + outcomeChange >= 10:
      return 0
  return -outcomes[goal]

# ---
  
def getUtility3(goal, outcomes):
  sideEffects = 0
  for outcomeGoal, outcomeChange in outcomes.items():
    if goals[outcomeGoal] + outcomeChange >= 10:
      return 0
    elif outcomeGoal != goal:
      sideEffects += outcomeChange
  return -outcomes[goal] + sideEffects
  
# ---

def chooseBestAction(goal):
  result = None
  bestUtility = None
  for action, outcomes in actions.items():
    if goal in outcomes:
      utility = getUtility(goal, outcomes)
      if result == None or utility > bestUtility:
        result = action
        bestUtility = utility
  return result
  
# ---

def executeAction(action):
  for goal in actions[action]:
    goals[goal] += actions[action][goal]
    if goals[goal] > 10:
      goals[goal] = 10
  
# ---

while not goalsAchieved():

  printGoalValues()
    
  goal = chooseMostImportantGoal()
  action = chooseBestAction(goal)
    
  print()
  print('Goal: ' + goal)
  print('Action: ' + action)
  
  executeAction(action)
  
  if goalFailed():
    break
  
  time.sleep(0.2)
  

printGoalValues()
print()
print('Goal: ' + goal)
print('Action: ' + action)