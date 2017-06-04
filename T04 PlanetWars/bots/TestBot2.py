from random import choice

class TestBot2(object):
  
  def update(self, gameInfo):
      
    if gameInfo.my_planets and gameInfo.not_my_planets:
      
      possibleDestinations = list(filter(lambda x: x.id not in map(lambda x: x.dest.id, gameInfo.my_fleets.values()), gameInfo.not_my_planets.values()))
      
      if len(possibleDestinations) == 0:
        return
      
      src  = max(gameInfo.my_planets.values(), key = lambda x: x.num_ships)
      
      maxDistVal  = max(possibleDestinations, key = lambda x: x.distance_to(src)).distance_to(src)
      maxShipsVal = max(possibleDestinations, key = lambda x: x.num_ships).num_ships
      
      dest = min(possibleDestinations, key = lambda x: (x.distance_to(src)/maxDistVal) + (x.num_ships/(maxShipsVal+1)))
   
      if src.num_ships > 10:
        gameInfo.planet_order(src, dest, int(src.num_ships * 0.75))