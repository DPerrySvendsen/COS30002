class TacticalBot_v3 (object):

    # TODO: TacticalBot_v4 needs to take into account the fleets we've already sent, so that we don't double up

    def update(self, gameInfo):

        print(len(gameInfo.enemy_fleets))

        if not gameInfo.my_planets or not gameInfo.not_my_planets:
            return

        # Record the current and required ships for each planet
        planet_details = {}
        for planet_id, planet in gameInfo.planets.items():
            planet_details[planet_id] = {
                'ID': planet_id,
                # Who owns this planet?
                'owner': 'me' if planet_id in gameInfo.my_planets else ('enemy' if planet_id in gameInfo.enemy_planets else 'neutral'),
                # How many ships are there?
                'ships_current': planet.num_ships,
                # If this is a our planet, how many ships are required to defend it?
                # If this is not our planet, how many ships would be required to capture it?
                'ships_required': 0 if planet_id in gameInfo.my_planets else planet.num_ships
            }

        # Adjust the required ships figure to reflect the movement of enemy fleets
        for enemy_fleet in gameInfo.enemy_fleets.values():
            # Fleet is attacking one of our planets, record the number of ships needed to defend
            # Fleet is capturing a neutral planet or reinforcing an enemy planet, adjust the number of ships needed to capture it
            planet_details[enemy_fleet.dest.id]['ships_required'] += enemy_fleet.num_ships

        # Get list of all my planets that could send ships to attack or defend (leaving at least 10 ships at home)
        my_available_planets = list(filter(lambda planet: planet['owner'] == 'me' and planet['ships_required'] < planet['ships_current'], planet_details.values()))

        # Get list of all my planets where more ships are required to defend
        my_planet_details = list(filter(lambda planet: planet['owner'] == 'me' and planet['ships_required'] > planet['ships_current'], planet_details.values()))
        fleets_requested = []
        for my_planet in my_planet_details:
            # For each such planet, request a defensive fleet
            fleets_requested.append({
                'planet': my_planet,
                'required': my_planet['ships_required'] - my_planet['ships_current']
            })

        # Sort the requests by the number of ships required, lowest to highest
        defensive_fleets_requested = sorted(fleets_requested, key = lambda request: request['required'], reverse = True)

        # Evaluate each request and send a fleet if possible
        self.send_fleets(gameInfo, defensive_fleets_requested, my_available_planets)

        # Get list of all neutral planets we could capture
        not_my_planet_details = list(filter(lambda planet: planet['owner'] == 'neutral', planet_details.values()))
        fleets_requested = []
        for not_my_planet in not_my_planet_details:
            # For each such planet, request a fleet
            fleets_requested.append({
                'planet': not_my_planet,
                'required': not_my_planet['ships_required']
            })

        # Sort the requests by the number of ships required, lowest to highest
        capturing_fleets_requested = sorted(fleets_requested, key = lambda request: request['required'], reverse = True)

        # Evaluate each request and send a fleet if possible
        self.send_fleets(gameInfo, capturing_fleets_requested, my_available_planets)

        # Get list of all enemy planets we could attack
        enemy_planet_details = list(filter(lambda planet: planet['owner'] == 'enemy', planet_details.values()))
        fleets_requested = []
        for enemy_planet in enemy_planet_details:
            # For each such planet, request an attack fleet
            fleets_requested.append({
                'planet': enemy_planet,
                'required': enemy_planet['ships_required']
            })

        # Sort the requests by the number of ships required, lowest to highest
        attacking_fleets_requested = sorted(fleets_requested, key = lambda request: request['required'], reverse = True)

        # Evaluate each request and send a fleet if possible
        self.send_fleets(gameInfo, attacking_fleets_requested, my_available_planets)

    # ---

    def send_fleets(self, gameInfo, requests, available_planets):

        max_distance = 10

        # Attempt to match each request to a planet with sufficient ships to launch a fleet
        for request in requests:
            for available_planet in available_planets:
                # Calculate the distance between the two planets
                distance_to = gameInfo.my_planets[available_planet['ID']].distance_to(
                    gameInfo.planets[request['planet']['ID']]
                )
                # Calculate the amount of ships that could be sent to attack
                available_ships = \
                    available_planet['ships_current'] - \
                    available_planet['ships_required']

                required_ships = request['required']

                if request['planet']['ID'] in gameInfo.enemy_planets:
                    # Calculate how many enemy ships will be created in the time it takes our fleet to reach the destination
                    required_ships += distance_to * gameInfo.planets[request['planet']['ID']].growth_rate

                # If the available planet has sufficient ships and if it's close enough, send a fleet
                if available_ships > required_ships and distance_to < max_distance:
                    gameInfo.planet_order(
                        gameInfo.my_planets[available_planet['ID']],
                        gameInfo.planets[request['planet']['ID']],
                        required_ships
                    )
                    available_planet['ships_current'] -= required_ships
                    break