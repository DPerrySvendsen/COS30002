import os
import time
import random

energy  = 100
boredom = 0
GPA     = 50

state = 'studying'

while True:
  time.sleep(0.05)
  os.system('cls')
  
  print('State   = '+state)
  print('Energy  = '+str(energy))
  print('Boredom = '+str(boredom))
  print('GPA     = '+str(GPA/25))
  
  if state == 'studying':
    energy  -= 1
    boredom += 1
    GPA     += 2
    if GPA >= 100 or energy < 30:
      state = 'sleeping'
    elif boredom > 70:
      state = 'partying'
      
  elif state == 'partying':
    energy  -= 1
    boredom -= 2
    GPA     -= 1
    if boredom <= 0 or GPA < 30:
      state = 'studying'
    elif energy < 30:
      state = 'sleeping'
      
  elif state == 'sleeping':
    energy  += 2
    boredom += 1  
    GPA     -= 1
    if energy >= 100 or boredom > 70:
      state = 'partying'
    elif GPA < 30:
      state = 'studying'