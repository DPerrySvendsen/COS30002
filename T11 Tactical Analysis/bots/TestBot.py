from random import choice

class TestBot(object):
  
  def update(self, gameInfo):
      
    if gameInfo.my_planets and gameInfo.not_my_planets:
      
      # All destinations that don't have a fleet going there yet
      possibleDestinations = list(filter(lambda x: x.id not in map(lambda x: x.dest.id, gameInfo.my_fleets.values()), gameInfo.not_my_planets.values()))
      
      if len(possibleDestinations) == 0:
        return
      
      dest = min(possibleDestinations,         key = lambda x: x.num_ships)
      src  = max(gameInfo.my_planets.values(), key = lambda x: x.num_ships)
   
      # If we have enough ships at the source planet, launch a fleet
      if src.num_ships > 10:
        gameInfo.planet_order(src, dest, int(src.num_ships * 0.75))