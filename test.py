
from random import randint, random

amount_of_cars = 7
                    #north, west, south, east
#fixedPositions = [(0,40),(40,0),(89,44),(44,89)]
finalCars = []

north_positions = {}
west_positions = {}
east_positions = {}
south_positions = {}

for car in range(amount_of_cars):
    selected_index = randint(0,3)
    #north
    if selected_index == 0:
        new_position = (randint(0,30),40)
        while new_position in north_positions:
            new_position = (randint(0,30),40)
        finalCars.append(new_position)
    #west
    elif selected_index == 1:
        new_position =  (40,randint(0,30))
        while new_position in west_positions:
            new_position = (40,randint(0,30))
        finalCars.append(new_position)
    #south
    elif selected_index == 2:
        new_position =  (randint(59,89),44)
        while new_position in south_positions:
            new_position = (randint(59,89),44)
        finalCars.append(new_position)
    #east
    elif selected_index == 3:
        new_position =  (44,randint(59,89))
        while new_position in south_positions:
            new_position = (44,randint(59,89))
        finalCars.append(new_position)

print(finalCars)
        


