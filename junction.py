# Agent model library
import agentpy as ap
# Random
from random import randint, choice

class junctionModel(ap.Model):
    def setup(self):
        # Minimum amount of cars
        if self.p.cars < 5: self.p.cars = 5
        # Minimum dimensions
        if self.p.height < 7: self.p.height = 7
        if self.p.width < 7: self.p.width = 7
        # Odd dimensions
        if self.p.width % 2 == 0: self.p.width += 1
        if self.p.height % 2 == 0: self.p.height += 1
        # Maximum amount of cars given lane space
        lane_cells = self.p.height + self.p.width - 6
        self.p.cars = self.p.cars if self.p.cars <= lane_cells else lane_cells

        # Coordinates of center cell
        center = (int(self.p.height / 2), int(self.p.width / 2))

        north_positions = set()
        west_positions = set()
        east_positions = set()
        south_positions = set()
        for car in range(self.p.cars):
            # north-bound
            if car % 4 == 0:
                new_position =  (randint(center[0] + 2, self.p.height - 1), center[1])
                while new_position in north_positions:
                    new_position = (randint(center[0] + 2, self.p.height - 1), center[1])
                north_positions.add(new_position)
            # west-bound
            elif car % 4 == 1:
                new_position = (center[0], randint(center[1] + 2, self.p.width - 1))
                while new_position in west_positions:
                    new_position = (center[0], randint(center[1] + 2, self.p.width - 1))
                west_positions.add(new_position)
            # south-bound
            elif car % 4 == 2:
                new_position =  (randint(0, center[0] - 2), center[1])
                while new_position in south_positions:
                    new_position = (randint(0, center[0] - 2), center[1])
                south_positions.add(new_position)
            # east-bound
            elif car % 4 == 3:
                new_position =  (center[0], randint(0, center[1] - 2))
                while new_position in east_positions:
                    new_position = (center[0], randint(0, center[1] - 2))
                east_positions.add(new_position)

        grass_positions = [center]
        # upper left quarter
        for i in range(0, center[0] - 1):
            for j in range(0, center[1]):
                grass_positions.append((i, j))
        # lower left quarter
        for i in range(center[0] + 1, self.p.height):
            for j in range(0, center[1] - 1):
                grass_positions.append((i,j))
        # upper right quarter
        for i in range(0, center[0]):
            for j in range(center[1] + 2, self.p.width):
                grass_positions.append((i,j))
        # lower right quarter
        for i in range(center[0] + 2, self.p.height):
            for j in range(center[1] + 1, self.p.width):
                grass_positions.append((i,j))

        # Create agents (cars and sidewalks)
        cars_n = ap.AgentList(self, len(north_positions))
        cars_w = ap.AgentList(self, len(west_positions))
        cars_s = ap.AgentList(self, len(south_positions))
        cars_e = ap.AgentList(self, len(east_positions))
        grass = ap.AgentList(self, len(grass_positions))
        intersection_agents = ap.AgentList(self, 8)

        cars_n.status = 0
        cars_w.status = 5
        cars_s.status = 10
        cars_e.status = 15
        grass.status = 20
        # for status, agent in zip(range(21, 29), intersection_agents):
        #     agent.status = status

        self.agents = grass
        self.agents.extend(cars_n)
        self.agents.extend(cars_w)
        self.agents.extend(cars_s)
        self.agents.extend(cars_e)
        # self.agents.extend(intersection_agents)

        self.ground = ap.Grid(self, (self.p.height, self.p.width), track_empty = True, check_border = True)
        self.ground.add_agents(grass, grass_positions, empty = False)
        self.ground.add_agents(cars_n, north_positions, empty = False)
        self.ground.add_agents(cars_w, west_positions, empty = False)
        self.ground.add_agents(cars_s, south_positions, empty = False)
        self.ground.add_agents(cars_e, east_positions, empty = False)
        # self.ground.add_agents(intersection_agents, intersection_positions, empty = False)
        
    def step(self):
        # Coordinates of center cell
        center = (int(self.p.height / 2), int(self.p.width / 2))
        
        entry_positions = [
            (center[0] + 1, center[1]), # north-bound
            (center[0], center[1] + 1), # west-bound
            (center[0] - 1, center[1]), # south-bound
            (center[0], center[1] - 1), # east-bound
        ]
        pre_entry_positions = [
            (center[0] + 2, center[1]), # north-bound
            (center[0], center[1] + 2), # west-bound
            (center[0] - 2, center[1]), # south-bound
            (center[0], center[1] - 2), # east-bound
        ]
        exit_positions = [
            (center[0] + 1, center[1] + 1), # east-bound
            (center[0] - 1, center[1] + 1), # north-bound
            (center[0] - 1, center[1] - 1), # west-bound
            (center[0] + 1, center[1] - 1), # south-bound
        ]

        #          y   x
        north = ( -1,  0 )
        west  = (  0, -1 )
        south = (  1,  0 )
        east  = (  0,  1 )
        moves = [north, west, south, east]

        # moving_cars = self.agents.select(self.agents.status < 20)
        moving_cars = list()
        # update cars in order:
        # 1. those about to enter
        # 2. those inside the roundabout
        for coord in pre_entry_positions + entry_positions + exit_positions:
            moving_cars.extend(list(self.ground.agents[coord]))
        # 3. those in the queue to enter (outwards)
        for i in range(1, center[0] - 1):
            for idx, (y, x) in enumerate(moves):
                moving_cars.extend(list(self.ground.agents[(
                    pre_entry_positions[(idx - 2) % 4][0] + y * i,
                    pre_entry_positions[(idx - 2) % 4][1] + x * i
                )]))
        # 4. exiting
        moving_cars.extend(list(self.ground.agents[
            center[0] + 2 : self.p.height - 1,
            center[1] - 1
        ]))
        moving_cars.extend(list(self.ground.agents[
            center[0] + 1,
            center[1] + 2 : self.p.width - 1
        ]))
        moving_cars.extend(list(self.ground.agents[
            0 : center[0] - 1,
            center[1] + 1
        ]))
        moving_cars.extend(list(self.ground.agents[
            center[0] - 1,
            0 : center[1] - 1
        ]))

        for car in moving_cars:
            if car.status % 5 == 0: # before entering
                car_origin = int(car.status / 5)
                if self.ground.positions[car] == entry_positions[car_origin]:
                    # turn right after entering
                    car.status += 1
                elif self.ground.positions[car] == pre_entry_positions[car_origin] and len(self.ground.agents[exit_positions[(car_origin - 1) % 4]]) > 0:
                    # wait to enter roundabout
                    # if there are cars in the roundabout
                    continue
                elif (self.ground.positions[car][0] > pre_entry_positions[0][0] \
                    or self.ground.positions[car][0] < pre_entry_positions[2][0] \
                    or self.ground.positions[car][1] > pre_entry_positions[1][1] \
                    or self.ground.positions[car][1] < pre_entry_positions[3][1]) \
                    and len(self.ground.agents[
                        self.ground.positions[car][0] + moves[car_origin][0],
                        self.ground.positions[car][1] + moves[car_origin][1],
                    ]) > 0:
                    # if there are cars in front
                    continue
                else:
                    # continue straight
                    self.ground.move_by(car, moves[car_origin])
            if car.status % 5 == 1: # inside roundabout
                car_origin = int(car.status / 5)
                if self.ground.positions[car] == exit_positions[car_origin % 4] and choice([0] + [1] * 3):
                    # turn left to skip exit (25% chance)
                    car.status += 1
                else:
                    # continue straight
                    self.ground.move_by(car, moves[(car_origin - 1) % 4])
            if car.status % 5 == 2: # skipped first exit
                car_origin = int(car.status / 5)
                if self.ground.positions[car] == exit_positions[(car_origin + 1) % 4] and choice([0] + [1] * 2):
                    # turn left to skip exit
                    car.status += 1
                else:
                    # continue straight
                    self.ground.move_by(car, moves[car_origin % 4])
            if car.status % 5 == 3: # skipped second exit
                car_origin = int(car.status / 5)
                if self.ground.positions[car] == exit_positions[(car_origin + 2) % 4] and choice([0, 1]):
                    # turn left to skip exit
                    car.status += 1
                else:
                    # continue straight
                    self.ground.move_by(car, moves[(car_origin + 1) % 4])
            if car.status % 5 == 4: # skipped third exit
                car_origin = int(car.status / 5)
                self.ground.move_by(car, moves[(car_origin + 2) % 4])