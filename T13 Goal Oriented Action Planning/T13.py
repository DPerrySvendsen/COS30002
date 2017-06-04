import sys
import os
import time
import copy

# ---

NL  = '\n'
TAB = '\t'

# ---

class GOAPState:
  
  def __init__(self, states):
    self.states = {}
    for state in states:
      self.set_state(state)
    
  # ---
  
  def set_state(self, name, initial_value = False):
    self.states[name] = initial_value
 
  # ---
  
  def preconditions_met(self, action):
  
    for precondition in action.preconditions:
      if self.states[precondition['State']] != precondition['Required']:
        return False
    return True
    
  # ---
  
  def perform_action(self, action):
  
    for effect in action.effects:
      self.states[effect['State']] = effect['Result']
      
  # ---
  
  def print_states(self):
  
    print(NL + 'Current states:' + NL)
    for state, value in self.states.items():
      print(TAB + '[' + ('*' if value else ' ') + '] ' + state)

# ---

class GOAPAction:

  def __init__(self, name, cost):
    
    self.name = name
    self.cost = cost
    self.preconditions = []
    self.effects = []
  
  # ---
  
  def setup_action(self, before, after, maintain_before_state = True):
    
    # A shorthand way to set up the preconditions and effects of the action
    
    # Can represent a gathering action (when maintain_before_state is True),
    # where, for example, the Agent can chop down a tree to obtain logs (the 
    # 'after' state) if it has an axe (the 'before' state) and doesn't already 
    # have logs. 
    
    # Can alternatively represent a crafting action (when maintain_before_state
    # is False), where, for example, the Agent can craft a stone axe (the 'after'
    # state) if it has stone and logs (the 'before' states) and dosn't already
    # have a stone axe. The only difference here is that performing this action
    # sets the 'before' state(s) back to False.
    
    for state in before:
      self.add_precondition(state)
      if not maintain_before_state:
        self.add_effect(state, False)
      
    for state in after:
      self.add_precondition(state, False)
      self.add_effect(state)
  
  # ---
  
  def add_precondition(self, precondition, required_value = True):
    
    self.preconditions.append({
      'State'    : precondition,
      'Required' : required_value
    })
  
  # ---
  
  def add_effect(self, effect, result_value = True):
  
    self.effects.append({
      'State'  : effect,
      'Result' : result_value
    })
    
# ---

class GOAPAgent:

  def __init__(self):
    
    self.state = []
    self.actions = []
    self.cost_so_far = 0

    self.paths_evaluated = 0
  
  # ---  
  
  def get_possible_actions(self, state = None):
 
    if not state:
      state = self.state
  
    return list(filter(lambda action: state.preconditions_met(action), self.actions))
  
  # ---
  
  def print_possible_actions(self):

    print(NL + 'Possible actions:' + NL)
    for action in self.get_possible_actions():
      print(TAB + action.name + ' (' + str(action.cost) + ')')
      
  # ---
  
  def perform_action(self, action):
  
    print(NL + 'Performing action:' + NL + NL + TAB + action.name)
    self.state.perform_action(action)
    self.cost_so_far += action.cost
  
  # ---
  
  def depth_first_search(
    self, 
    goal_state, 
    state          = None, 
    sequence       = None, 
    initial_action = None
  ):
  
    # Start by using the current state of the Agent
    if not state:
      state = copy.deepcopy(self.state)
 
    # The sequence represents the series of actions taken to reach 
    # the current state, as well as the total cost
    if not sequence:
      sequence = {
        'Actions' : [],
        'Cost'    : 0
      }
      self.paths_evaluated = 0
 
    # Has an initial action been defined?
    if initial_action:
      # If so, start by performing this action
      sequence['Actions'].append(initial_action)
      sequence['Cost'] += initial_action.cost
      state.perform_action(initial_action)
      
    # Have we reached the goal state?
    if state.states[goal_state]:

      self.paths_evaluated += 1
      path = ''
      for action in sequence['Actions']:
        path += action.name + ' -> '

      if self.paths_evaluated % 100 == 0:
        cls()
        print('Evaluating sequence #' + str(self.paths_evaluated) + '...' + NL)
        print('Cost: ' + str(sequence['Cost']))
        print('Sequence: ' + path[:-3])
      
      # If so, return the sequence we used to reach this point
      return sequence
      
    # If not, get all possible actions
    possible_actions = self.get_possible_actions(state)
 
    lowest_cost_sequence = None
 
    for action in possible_actions:
      # Try all possible actions
      possible_sequence = self.depth_first_search(
        goal_state, 
        copy.deepcopy(state), 
        copy.deepcopy(sequence), 
        action
      )
      # Find the action that produces the lowest-cost sequence
      if not lowest_cost_sequence or possible_sequence['Cost'] < lowest_cost_sequence['Cost']:
        lowest_cost_sequence = possible_sequence

    # Return this sequence
    return lowest_cost_sequence
      
# ---

def cls():
  # Clear the console and print a newline
  os.system('cls')
  print()
  
# ---

# Actions
punch_tree       = GOAPAction('Punch tree',                     100)
craft_wood_axe   = GOAPAction('Craft wooden axe',                10)
craft_wood_pick  = GOAPAction('Craft wooden pickaxe',            10)
craft_stone_axe  = GOAPAction('Craft stone axe',                 10)
craft_stone_pick = GOAPAction('Craft stone pickaxe',             10)
chop_wood_wood   = GOAPAction('Chop wood with wooden axe',       40)
chop_wood_stone  = GOAPAction('Chop wood with stone axe',        20)
mine_stone_wood  = GOAPAction('Mine stone with wooden pickaxe',  40)
mine_stone_stone = GOAPAction('Mine stone with stone pickaxe',   20)
mine_iron_stone  = GOAPAction('Mine iron with stone pickaxe',    20)

# Crafting
craft_wood_axe  .setup_action(['HasLogs'],             ['HasWoodAxe'],   False)
craft_wood_pick .setup_action(['HasLogs'],             ['HasWoodPick'],  False)
craft_stone_axe .setup_action(['HasLogs', 'HasStone'], ['HasStoneAxe'],  False)
craft_stone_pick.setup_action(['HasLogs', 'HasStone'], ['HasStonePick'], False)

# Gathering
punch_tree      .setup_action([],               ['HasLogs'])
chop_wood_wood  .setup_action(['HasWoodAxe'],   ['HasLogs'])
chop_wood_stone .setup_action(['HasStoneAxe'],  ['HasLogs'])
mine_stone_wood .setup_action(['HasWoodPick'],  ['HasStone'])
mine_stone_stone.setup_action(['HasStonePick'], ['HasStone'])
mine_iron_stone .setup_action(['HasStonePick'], ['HasIron'])
 
agent = GOAPAgent()

agent.state = GOAPState([
  'HasLogs',
  'HasStone',
  'HasIron',
  'HasWoodAxe',
  'HasWoodPick',
  'HasStoneAxe',
  'HasStonePick'
])

agent.actions = [
  punch_tree,     
  craft_wood_axe,  
  craft_wood_pick, 
  craft_stone_axe, 
  craft_stone_pick,
  chop_wood_wood,  
  chop_wood_stone, 
  mine_stone_wood, 
  mine_stone_stone,
  mine_iron_stone     
]

# ---

# Perform a depth-first search to find the optimal sequence of actions

goal_state = 'HasIron'
sequence = agent.depth_first_search(goal_state)

# Display the results

cls()
print('Goal: ' + goal_state + NL)
for i in range(len(sequence['Actions'])):
  print(str(i+1) + '. ' + sequence['Actions'][i].name + ' (' + str(sequence['Actions'][i].cost) + ')')

print(NL + 'Total cost: ' + str(sequence['Cost']))  
  
input(NL + 'Press any key to continue...')  

# Perform the sequence of actions
  
for action in sequence['Actions']:

  cls()
  print('Goal: ' + goal_state)
  print('Cost: ' + str(agent.cost_so_far))
  
  agent.state.print_states()
  agent.print_possible_actions()
  input(NL + 'Press any key to continue...')  
  
  agent.perform_action(action)
  input(NL + 'Press any key to continue...')  
 
# Display the end states 
 
cls()
print('Goal: ' + goal_state)
print('Cost: ' + str(agent.cost_so_far))

agent.state.print_states()