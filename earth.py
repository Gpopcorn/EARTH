from operator import itemgetter
from math import sin, cos, sqrt
from random import randint
from copy import deepcopy
import pygame
import time










def multiply_matrix(a, b):
    rowsA = len(a)
    colsA = len(a[0])
    rowsB = len(b)
    colsB = len(b[0])

    c = [[0 for row in range(colsB)] for col in range(rowsA)]

    for x in range(rowsA):
        for y in range(colsB):
            for z in range(colsA):
                c[x][y] += a[x][z] * b[z][y]

    return c

# WORK IN PROGRESS
# ----------------------------------------------------------------
def load_obj(file):
    try:
        content = open(file, 'r').read()
    except TypeError:
        print("An error has occured.")
        exit()
    content_lines = content.split('\n')
    verticies = []
    faces = []

    for line in content_lines:
        if line.startswith('f '):
            line = line.split(' ')
            line.pop(0)
            line_list = []
            for index, face in enumerate(line):
                if face == '':
                    line.remove(face)
                else:
                    face = face.replace('//', '/')
                    line[index] = list(map(int, face.split('/')))[0] - 1
                    line_list.append(line[index])

            faces.append(line_list)

        elif line.startswith('v '):
            line = line.replace('  ', ' ')
            line = line.split(' ')
            line.pop(0)
            line = list(map(float, line))
            for index, item in enumerate(line):
                line[index] = [item]
            verticies.append(line)

    return (verticies, faces)
# ----------------------------------------------------------------

def in_range(position_1, position_2, radius):
    if position_1[0][0] > position_2[0][0] - radius and position_1[0][0] < position_2[0][0] + radius:
        if position_1[1][0] > position_2[1][0] - radius and position_1[1][0] < position_2[1][0] + radius:
            if position_1[2][0] > position_2[2][0] - radius and position_1[2][0] < position_2[2][0] + radius:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


class Light():
    def __init__(self, position, radius, intensity):
        self.position = position
        self.radius = radius
        self.intensity = intensity

class Camera():
    def __init__(self, x_rotation, y_rotation, z_rotation, fov, center, distance):
        self.x_rotation = x_rotation
        self.y_rotation = y_rotation
        self.z_rotation = z_rotation

        self.fov = fov
        self.center = center
        self.distance = distance


    def rotate_x(self, amount):
        self.x_rotation += amount
    
    def rotate_y(self, amount):
        self.y_rotation += amount

    def rotate_z(self, amount):
        self.z_rotation += amount

    def change_distance(self, amount):
        self.distance += amount

class Engine():
    def __init__(self):
        self.pointsZ = []

    def do_3d_math(self, points, camera):
        rotation_x_matrix = [[1, 0, 0], [0, cos(camera.x_rotation), -sin(camera.x_rotation)], [0, sin(camera.x_rotation), cos(camera.x_rotation)]]
        rotation_y_matrix = [[cos(camera.y_rotation), 0, -sin(camera.y_rotation)], [0, 1, 0], [sin(camera.y_rotation), 0, cos(camera.y_rotation)]]
        rotation_z_matrix = [[cos(camera.z_rotation), -sin(camera.z_rotation), 0], [sin(camera.z_rotation), cos(camera.z_rotation), 0], [0, 0, 1]]

        return_list = [p for p in range(len(points))]
        self.pointsZ = [0 for p in range(len(points))]
        for index, point in enumerate(points):
            rotated = multiply_matrix(rotation_x_matrix, point)
            rotated = multiply_matrix(rotation_y_matrix, rotated)
            rotated = multiply_matrix(rotation_z_matrix, rotated)
            if camera.distance != 0:
                z = 1/(camera.distance - rotated[2][0])
            else:
                z = 0
            projection = [[z, 0, 0], [0, z, 0]]

            projected = multiply_matrix(projection, rotated)

            x = projected[0][0] * camera.fov + camera.center[0]
            y = projected[1][0] * camera.fov + camera.center[1]

            return_list[index] = [x, y]

            self.pointsZ[index] = z

        return return_list

    def do_light_math(self, faces, points, light):
        new_faces = deepcopy(faces)
        for index, face in enumerate(new_faces):
            face_point_list = []
            for point in face:
                if type(point) == int:
                    face_point_list.append(points[point])

            x_list = []
            y_list = []
            z_list = []

            for point in face_point_list:
                x_list.append(point[0][0])
                y_list.append(point[1][0])
                z_list.append(point[2][0])

            if len(x_list) == 4:
                face_point_average = [[(x_list[0] + x_list[1] + x_list[2] + x_list[3]) / 4], [(y_list[0] + y_list[1] + y_list[2] + y_list[3]) / 4], [(z_list[0] + z_list[1] + z_list[2] + z_list[3]) / 4]]
            elif len(x_list) == 3:
                face_point_average = [[(x_list[0] + x_list[1] + x_list[2]) / 3], [(y_list[0] + y_list[1] + y_list[2]) / 3], [(z_list[0] + z_list[1] + z_list[2]) / 3]]

            change = 0

            if in_range(face_point_average, light.position, light.radius) == True:
                distance_between = sqrt((light.position[0][0] - face_point_average[0][0]) ** 2 + (light.position[1][0] - face_point_average[1][0]) ** 2 + (light.position[2][0] - face_point_average[2][0]) ** 2)
                if distance_between == 0:
                    distance_between = 0.01
                change = round(light.intensity / distance_between)

            if len(x_list) == 4:
                new_faces[index][4] = (face[4][0] + change, face[4][1] + change, face[4][2] + change)
            elif len(x_list) == 3:
                new_faces[index][3] = (face[3][0] + change, face[3][1] + change, face[3][2] + change)

            if len(x_list) == 4:
                temp_list = list(new_faces[index][4])
                if temp_list[0] > 255:
                    temp_list[0] = 255
                elif temp_list[0] < 0:
                    temp_list[0] = 0
                if temp_list[1] > 255:
                    temp_list[1] = 255
                elif temp_list[1] < 0:
                    temp_list[1] = 0
                if temp_list[2] > 255:
                    temp_list[2] = 255
                elif temp_list[2] < 0:
                    temp_list[2] = 0
                new_faces[index][4] = tuple(temp_list)
            elif len(x_list) == 3:
                temp_list = list(new_faces[index][3])
                if temp_list[0] > 255:
                    temp_list[0] = 255
                elif temp_list[0] < 0:
                    temp_list[0] = 0
                if temp_list[1] > 255:
                    temp_list[1] = 255
                elif temp_list[1] < 0:
                    temp_list[1] = 0
                if temp_list[2] > 255:
                    temp_list[2] = 255
                elif temp_list[2] < 0:
                    temp_list[2] = 0
                new_faces[index][3] = tuple(temp_list)
                
        return new_faces

    def sort_faces(self, faces):
        return_list = deepcopy(faces)
        for face in return_list:
            faceZ = []
            for value in face:
                if isinstance(value, int) == True:
                    faceZ.append(self.pointsZ[value])

            face.append(faceZ)

            if len(face) == 6:
                face.append(sum([face[5][0], face[5][1], face[5][2], face[5][3]]) / 4)
            elif len(face) == 5:
                face.append("placeholder")
                face.append(sum([face[4][0], face[4][1], face[4][2]]) / 3)

        return_list.sort(key=itemgetter(6))

        for face in return_list:
            if "placeholder" in face:
                face.remove("placeholder")

            face.pop()
            face.pop()

        return return_list










# greyscale
BLACK              = (0  , 0  , 0  )
DARK_GRAY          = (75 , 75 , 75 )
WHITE              = (255, 255, 255)

# basic colors
GREEN              = (0  , 255, 0  )
BLUE               = (0  , 0  , 255)
YELLOW             = (255, 255, 0  )

# special colors
DARKER_BLUE        = (0  , 0  , 100)
DARK_BLUE          = (0  , 0  , 150)
LIGHT_BLUE         = (75 , 125, 255)
LIGHTER_BLUE       = (150, 200, 255)
LIGHTEST_BLUE      = (190, 225, 255)

GRAY_BLUE          = (225, 235, 255)
DARK_GRAY_BLUE     = (170, 205, 225)

DARKER_GREEN       = (0  , 100, 0  )
DARK_GREEN         = (0  , 150, 0  )

DARK_RED           = (150, 0  , 0  )

DARK_YELLOW        = (150, 150, 0  )

DARK_BROWN         = (65 , 15 , 0  )
BROWN              = (140, 82 , 45 )










ICO_SPHERE = load_obj('objects/Sphere.obj')
ICO_SPHERE_V = ICO_SPHERE[0]
ICO_SPHERE_F = ICO_SPHERE[1]










def area(a, b, c):
    return abs((a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1])) / 2.0)

def is_inside(a, b, c, d):
    e = area(a, b, c) + 0.1
    f = area(d, b, c)
    g = area(a, d, c)
    h = area(a, b, d)

    if e >= f + g + h:
        return True
    else:
        return False










def generate_terrain(tiles):
    terrain = []
    last_generation = 1

    i = 0
    for i in range(0, tiles):
        if last_generation > -3 and last_generation < 3:
            rdm = randint(last_generation - 1, last_generation + 1)
            terrain.append(rdm)
            last_generation = rdm
        if last_generation == -3:
            rdm = randint(last_generation, last_generation + 2)
            terrain.append(rdm)
            last_generation = rdm
        if last_generation == 3:
            rdm = randint(last_generation - 2, last_generation)
            terrain.append(rdm)
            last_generation = rdm
            
        i += 1

    return terrain










mouse_sensitivity = 0.02
scroll_sensitivity = 0.5

max_distance = 20
min_distance = 10










pygame.font.init()
freesansbold20 = pygame.font.Font('freesansbold.ttf', 20)

class Action_Text():
    def __init__(self, display, text, duration, pos=(300, 25), color=DARK_RED):
        self.display = display
        self.text = text
        self.duration = duration
        self.pos = pos
        self.color = color

        self.frame = 0

    def show(self):
        self.frame = self.duration * 60

    def next_frame(self):
        if self.frame > 0:
            self.frame -= 1
        if self.frame > 0:
            self.display.blit(freesansbold20.render(self.text, True, self.color), self.pos)










class Push_Button():
    def __init__(self, rect, screen):
        self.rect = rect
        self.screen = screen

        self.hover = False
        self.click = False

    def draw(self):
        if self.hover == True:
            if self.click == True:
                pygame.draw.rect(self.screen, DARK_GRAY_BLUE, self.rect)
            else:
                pygame.draw.rect(self.screen, GRAY_BLUE, self.rect)
        else:
            pygame.draw.rect(self.screen, LIGHTEST_BLUE, self.rect)










_gameversion = 'V1.0'

engine = Engine()
camera = Camera(50, 50, 0, 500, (500, 350), 12)
light = Light([[20], [0], [0]], 50, 1500)


pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("E A R T H - " + _gameversion)

clock = pygame.time.Clock()

freesansbold30 = pygame.font.Font('freesansbold.ttf', 30)
freesansbold15 = pygame.font.Font('freesansbold.ttf', 15)

population_symbol = pygame.image.load('sprites/Population.png')
water_symbol = pygame.image.load('sprites/Water.png')
rock_symbol = pygame.image.load('sprites/Rock.png')
wood_symbol = pygame.image.load('sprites/Wood.png')
population_symbol_small = pygame.image.load('sprites/Population_Small.png')
water_symbol_small = pygame.image.load('sprites/Water_Small.png')
rock_symbol_small = pygame.image.load('sprites/Rock_Small.png')
wood_symbol_small = pygame.image.load('sprites/Wood_Small.png')


not_enough_resources = Action_Text(screen, "You don't have enough resources to do that!", 2)
cant_start_day = Action_Text(screen, "You cannot start a new day!", 2, pos=(350, 25))


right_click = False
prev_mouse = (0, 0)


terrain = generate_terrain(80)
habitat_tile = randint(0, 79)
terrain[habitat_tile] = 4
color_list = []
for tile in terrain:
    if tile == -3 or tile == -2 or tile == -1:
        color_list.append(BLUE)
    elif tile == 0:
        color_list.append(DARK_YELLOW)
    elif tile == 1 or tile == 2 or tile == 3:
        color_list.append(DARK_GREEN)
    elif tile == 4:
        color_list.append(DARK_BROWN)

tile_list = []
for tile in terrain:
    tile_info = []
    if tile == -3:
        tile_info.append('Water')
        tile_info.append(randint(100, 150))
    if tile == -2:
        tile_info.append('Water')
        tile_info.append(randint(50, 100))
    elif tile == -1:
        tile_info.append('Water')
        tile_info.append(randint(4, 50))
    elif tile == 0:
        tile_info.append('Sand')
        tile_info.append(randint(4, 100))
    elif tile == 1:
        tile_info.append('Forest')
        tile_info.append(randint(4, 50))
    elif tile == 2:
        tile_info.append('Forest')
        tile_info.append(randint(50, 100))
    elif tile == 3:
        tile_info.append('Forest')
        tile_info.append(randint(100, 150))
    elif tile == 4:
        tile_info.append('Habitat')
        tile_info.append(0)
    tile_info.append(False)
    tile_list.append(tile_info)


harvest_button_r = pygame.Rect((25, 100), (120, 40))
harvest_button_t = freesansbold15.render('Instant Harvest', True, BLACK)
harvest_button = Push_Button(harvest_button_r, screen)

dangerous_harvest_button_r = pygame.Rect((25, 165), (120, 60))
dangerous_harvest_button_t = freesansbold15.render('Danger Harvest', True, BLACK)
dangerous_harvest_button = Push_Button(dangerous_harvest_button_r, screen)

smart_harvest_button_r = pygame.Rect((25, 250), (120, 80))
smart_harvest_button_t = freesansbold15.render('Smart Harvest', True, BLACK)
smart_harvest_button = Push_Button(smart_harvest_button_r, screen)

build_button_r = pygame.Rect((25, 100), (120, 80))
build_button_t = freesansbold15.render('Build Habitat', True, BLACK)
build_button = Push_Button(build_button_r, screen)

plant_button_r = pygame.Rect((25, 205), (120, 60))
plant_button_t = freesansbold15.render('Plant Forest', True, BLACK)
plant_button = Push_Button(plant_button_r, screen)

new_day_r = pygame.Rect((840, 450), (160, 40))
new_day_t = freesansbold15.render('Start New Day', True, BLACK)
new_day = Push_Button(new_day_r, screen)

end_game_r = pygame.Rect((400, 650), (200, 50))
end_game_t = freesansbold30.render('End Game', True, BLACK)
end_game = Push_Button(end_game_r, screen)


end_game_screen = False
end_game_screen_r = pygame.Rect((350, 250), (300, 200))
end_game_screen_t = freesansbold30.render('Game Over!', True, BLACK)


edges = []

tile_menu = [False, 0]

water = 0
wood  = 0
rock = 0

population = 5
max_population = 5

day = 0

start_time = time.time()
time_ended = False

run = True
while run:
    clock.tick(60)
    screen.fill(LIGHTER_BLUE)

    verticies = engine.do_3d_math(ICO_SPHERE_V, camera)

    unsorted_faces = deepcopy(ICO_SPHERE_F)
    for i, face in enumerate(unsorted_faces):
        face.append(color_list[i])
    color_faces = engine.do_light_math(unsorted_faces, ICO_SPHERE_V, light)

    faces = engine.sort_faces(color_faces)

    for face in faces:
        if len(face) == 4:
            pygame.draw.polygon(screen, face[3], (verticies[face[0]], verticies[face[1]], verticies[face[2]]))

    for edge in edges:
        pygame.draw.line(screen, WHITE, verticies[edge[0]], verticies[edge[1]], 4)

    wood_t = freesansbold30.render(str(wood), True, BLACK)
    rock_t = freesansbold30.render(str(rock), True, BLACK)
    water_t = freesansbold30.render(str(water), True, BLACK)
    population_t = freesansbold30.render(str(population) + "/" + str(max_population), True, BLACK)

    new_day_p = population // 2
    if new_day_p < 0:
        new_day_p = 0
    if max_population - population < new_day_p:
        new_day_p = max_population - population

    new_day_p_t = freesansbold15.render("+" + str(new_day_p), True, DARK_GREEN)
    new_day_w_t = freesansbold15.render("-" + str(population * 3), True, DARK_RED)
    new_day_f_t = freesansbold15.render("-" + str(population), True, DARK_RED)

    day_t = freesansbold30.render("Day " + str(day), True, BLACK)

    pygame.draw.polygon(screen, LIGHTEST_BLUE, ((840, 515), (1000, 515), (1000, 700), (840, 700)))
    screen.blit(population_symbol, (850, 650))
    screen.blit(water_symbol, (850, 600))
    screen.blit(rock_symbol, (850, 560))
    screen.blit(wood_symbol, (850, 520))

    screen.blit(water_t, (900, 615))
    screen.blit(rock_t, (900, 575))
    screen.blit(wood_t, (900, 535))
    screen.blit(population_t, (900, 665))

    new_day.draw()
    screen.blit(new_day_t, (870, 455))
    screen.blit(new_day_p_t, (845, 475))
    screen.blit(new_day_w_t, (900, 475))
    screen.blit(new_day_f_t, (955, 475))

    screen.blit(population_symbol_small, (870, 472))
    screen.blit(water_symbol_small, (925, 472))
    screen.blit(wood_symbol_small, (980, 472))

    end_game.draw()
    screen.blit(end_game_t, (425, 662))

    pygame.draw.polygon(screen, LIGHTEST_BLUE, ((840, 0), (1000, 0), (1000, 40), (840, 40)))
    screen.blit(day_t, (850, 5))

    if tile_menu[0] == True:
        pygame.draw.polygon(screen, LIGHTEST_BLUE, ((25, 25), (175, 25), (175, 75), (25, 75)))
        tile_type = freesansbold30.render(tile_list[tile_menu[1]][0], True, BLACK)
        resource_amount = freesansbold15.render(str(tile_list[tile_menu[1]][1]), True, BLACK)

        harvest_amount = freesansbold15.render("+" + str(round(tile_list[tile_menu[1]][1] / 4)), True, DARK_GREEN)
        dangerous_harvest_amount = freesansbold15.render("+" + str(round(tile_list[tile_menu[1]][1] - tile_list[tile_menu[1]][1] / 4)), True, DARK_GREEN)
        smart_harvest_amount = freesansbold15.render("+" + str(round(tile_list[tile_menu[1]][1])), True, DARK_GREEN)

        population_upgrade = freesansbold15.render("+5 Max", True, DARK_GREEN)

        resource_dangerous_harvest_p = freesansbold15.render("-2", True, DARK_RED)

        resource_smart_harvest = freesansbold15.render("-30", True, DARK_RED)

        resource_build_habitat_w = freesansbold15.render("-50", True, DARK_RED)
        resource_build_habitat_r = freesansbold15.render("-35", True, DARK_RED)

        resource_plant_forest_w = freesansbold15.render("-15", True, DARK_RED)
        resource_plant_forest_l = freesansbold15.render("-5", True, DARK_RED)

        screen.blit(tile_type, (30, 30))
        screen.blit(resource_amount, (30, 60))

        if tile_list[tile_menu[1]][0] != 'Empty' and tile_list[tile_menu[1]][0] != 'Habitat':
            harvest_button.draw()
            screen.blit(harvest_button_t, (30, 105))
            screen.blit(harvest_amount, (30, 125))

            dangerous_harvest_button.draw()
            screen.blit(dangerous_harvest_button_t, (28, 170))
            screen.blit(dangerous_harvest_amount, (30, 190))
            screen.blit(resource_dangerous_harvest_p, (30, 210))
            screen.blit(population_symbol_small, (54, 207))

            smart_harvest_button.draw()
            screen.blit(smart_harvest_button_t, (30, 255))
            screen.blit(smart_harvest_amount, (30, 275))
            screen.blit(resource_smart_harvest, (30, 295))
            screen.blit(resource_smart_harvest, (30, 315))


        elif tile_list[tile_menu[1]][0] == 'Empty':
            build_button.draw()
            screen.blit(build_button_t, (30, 105))
            screen.blit(population_upgrade, (30, 125))
            screen.blit(resource_build_habitat_w, (30, 145))
            screen.blit(resource_build_habitat_r, (30, 165))
            screen.blit(population_symbol_small, (90, 122))
            screen.blit(wood_symbol_small, (54, 142))
            screen.blit(rock_symbol_small, (54, 162))

            plant_button.draw()
            screen.blit(plant_button_t, (30, 210))
            screen.blit(resource_plant_forest_w, (30, 230))
            screen.blit(resource_plant_forest_l, (30, 250))
            screen.blit(wood_symbol_small, (54, 227))
            screen.blit(water_symbol_small, (54, 247))
        
        if tile_list[tile_menu[1]][0] == 'Water':
            screen.blit(water_symbol_small, (54, 57))
            screen.blit(water_symbol_small, (63, 122))
            screen.blit(water_symbol_small, (63, 187))
            screen.blit(water_symbol_small, (63, 272))
            screen.blit(rock_symbol_small, (63, 312))
            screen.blit(wood_symbol_small, (63, 292))
        elif tile_list[tile_menu[1]][0] == 'Sand':
            screen.blit(rock_symbol_small, (54, 57))
            screen.blit(rock_symbol_small, (63, 122))
            screen.blit(rock_symbol_small, (63, 187))
            screen.blit(water_symbol_small, (63, 312))
            screen.blit(rock_symbol_small, (63, 272))
            screen.blit(wood_symbol_small, (63, 292))
        elif tile_list[tile_menu[1]][0] == 'Forest':
            screen.blit(wood_symbol_small, (54, 57))
            screen.blit(wood_symbol_small, (63, 122))
            screen.blit(wood_symbol_small, (63, 187))
            screen.blit(water_symbol_small, (63, 292))
            screen.blit(rock_symbol_small, (63, 312))
            screen.blit(wood_symbol_small, (63, 272))


    if end_game_screen == True:
        end_game_screen_d = freesansbold30.render(str(day) + " Days", True, BLACK)
        end_game_screen_p = freesansbold30.render(str(population) + " Population", True, BLACK)
        if time_ended == False:
            seconds = round(time.time() - start_time)
            hours = seconds // (60*60)
            seconds %= (60*60)
            minutes = seconds // 60
            seconds %= 60
            end_game_screen_l = freesansbold30.render("%02i:%02i:%02i" % (hours, minutes, seconds), True, BLACK)
            time_ended = True
        pygame.draw.rect(screen, LIGHTEST_BLUE, end_game_screen_r)
        screen.blit(end_game_screen_t, (410, 275))
        screen.blit(end_game_screen_d, (400, 330))
        screen.blit(end_game_screen_p, (400, 360))
        screen.blit(end_game_screen_l, (400, 390))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            move_amount = (prev_mouse[0] - pos[0], prev_mouse[1] - pos[1])

            if end_game_screen == False:
                if right_click == True:
                    camera.rotate_x(move_amount[1] * mouse_sensitivity)
                    camera.rotate_y(move_amount[0] * mouse_sensitivity)

                if harvest_button_r.collidepoint(pos):
                    harvest_button.hover = True
                else:
                    harvest_button.hover = False

                if build_button_r.collidepoint(pos):
                    build_button.hover = True
                else:
                    build_button.hover = False

                if plant_button_r.collidepoint(pos):
                    plant_button.hover = True
                else:
                    plant_button.hover = False
                
                if dangerous_harvest_button_r.collidepoint(pos):
                    dangerous_harvest_button.hover = True
                else:
                    dangerous_harvest_button.hover = False

                if smart_harvest_button_r.collidepoint(pos):
                    smart_harvest_button.hover = True
                else:
                    smart_harvest_button.hover = False

                if new_day_r.collidepoint(pos):
                    new_day.hover = True
                else:
                    new_day.hover = False

                if end_game_r.collidepoint(pos):
                    end_game.hover = True
                else:
                    end_game.hover = False

            prev_mouse = pos

        harvest_button.click = False
        dangerous_harvest_button.click = False
        smart_harvest_button.click = False
        build_button.click = False
        plant_button.click = False
        new_day.click = False
        end_game.click = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if end_game_screen == False:
                    if harvest_button_r.collidepoint(event.pos):
                        if tile_list[tile_menu[1]][0] != 'Empty' and tile_list[tile_menu[1]][0] != 'Habitat':
                            harvest_button.click = True
                    if dangerous_harvest_button_r.collidepoint(event.pos):
                        if tile_list[tile_menu[1]][0] != 'Empty' and tile_list[tile_menu[1]][0] != 'Habitat':
                            dangerous_harvest_button.click = True
                    if smart_harvest_button_r.collidepoint(event.pos):
                        if tile_list[tile_menu[1]][0] != 'Empty' and tile_list[tile_menu[1]][0] != 'Habitat':
                            smart_harvest_button.click = True
                    if build_button_r.collidepoint(event.pos):
                        if tile_list[tile_menu[1]][0] == 'Empty':
                            build_button.click = True
                    if plant_button_r.collidepoint(event.pos):
                        if tile_list[tile_menu[1]][0] == 'Empty':
                            plant_button.click = True

                    if new_day_r.collidepoint(event.pos):
                        new_day.click = True
                    if end_game_r.collidepoint(event.pos):
                        end_game.click = True

                    if plant_button.click == False and harvest_button.click == False and build_button.click == False and dangerous_harvest_button.click == False and smart_harvest_button.click == False:
                        edges.clear()

                    clicked_faces = []
                    world_clicked = False
                    for face in faces:
                        if is_inside(verticies[face[0]], verticies[face[1]], verticies[face[2]], event.pos) == True:
                            clicked_faces.append(face)
                            world_clicked = True
                    if world_clicked == True:
                        edges.append([clicked_faces[len(clicked_faces) - 1][0], clicked_faces[len(clicked_faces) - 1][1]])
                        edges.append([clicked_faces[len(clicked_faces) - 1][0], clicked_faces[len(clicked_faces) - 1][2]])
                        edges.append([clicked_faces[len(clicked_faces) - 1][1], clicked_faces[len(clicked_faces) - 1][2]])
                        i = color_faces.index(clicked_faces[len(clicked_faces) - 1])
                        tile_menu[0] = True
                        tile_menu[1] = i
                    else:
                        if harvest_button.click == False and build_button.click == False and plant_button.click == False and dangerous_harvest_button.click == False and smart_harvest_button.click == False:
                            tile_menu[0] = False
                        

                if new_day.click == True:
                    if water >= population * 3 and wood >= population:
                        water -= population * 3
                        wood -= population
                        day += 1
                        population += new_day_p
                    else:
                        cant_start_day.show()

                if end_game.click == True:
                    end_game_screen = True

                if harvest_button.click == True:
                    if tile_menu[0] == True:
                        if tile_list[tile_menu[1]][0] == 'Water':
                            water += round(tile_list[tile_menu[1]][1] / 4)
                            tile_list[tile_menu[1]][0] = 'Sand'
                            tile_list[tile_menu[1]][1] = randint(4, 100)
                            color_list[tile_menu[1]] = DARK_YELLOW
                        elif tile_list[tile_menu[1]][0] == 'Sand':
                            rock += round(tile_list[tile_menu[1]][1] / 4)
                            tile_list[tile_menu[1]][0] = 'Empty'
                            tile_list[tile_menu[1]][1] = 0
                            color_list[tile_menu[1]] = BROWN
                        elif tile_list[tile_menu[1]][0] == 'Forest':
                            wood += round(tile_list[tile_menu[1]][1] / 4)
                            tile_list[tile_menu[1]][0] = 'Empty'
                            tile_list[tile_menu[1]][1] = 0
                            color_list[tile_menu[1]] = BROWN
                
                if dangerous_harvest_button.click == True:
                    if tile_menu[0] == True:
                        if population >= 2:
                            if tile_list[tile_menu[1]][0] == 'Water':
                                water += round(tile_list[tile_menu[1]][1] - tile_list[tile_menu[1]][1] / 4)
                                tile_list[tile_menu[1]][0] = 'Sand'
                                tile_list[tile_menu[1]][1] = randint(4, 100)
                                color_list[tile_menu[1]] = DARK_YELLOW
                            elif tile_list[tile_menu[1]][0] == 'Sand':
                                rock += round(tile_list[tile_menu[1]][1] - tile_list[tile_menu[1]][1] / 4)
                                tile_list[tile_menu[1]][0] = 'Empty'
                                tile_list[tile_menu[1]][1] = 0
                                color_list[tile_menu[1]] = BROWN
                            elif tile_list[tile_menu[1]][0] == 'Forest':
                                wood += round(tile_list[tile_menu[1]][1] - tile_list[tile_menu[1]][1] / 4)
                                tile_list[tile_menu[1]][0] = 'Empty'
                                tile_list[tile_menu[1]][1] = 0
                                color_list[tile_menu[1]] = BROWN

                            population -= 2
                        else:
                            not_enough_resources.show()

                if smart_harvest_button.click == True:
                    if tile_menu[0] == True:
                        if tile_list[tile_menu[1]][0] == 'Water':
                            if wood >= 30 and rock >= 30:
                                water += round(tile_list[tile_menu[1]][1])
                                tile_list[tile_menu[1]][0] = 'Sand'
                                tile_list[tile_menu[1]][1] = randint(4, 100)
                                color_list[tile_menu[1]] = DARK_YELLOW
                                wood -= 30
                                rock -= 30
                            else:
                                not_enough_resources.show()
                        elif tile_list[tile_menu[1]][0] == 'Forest':
                            if water >= 30 and rock >= 30:
                                wood += round(tile_list[tile_menu[1]][1])
                                tile_list[tile_menu[1]][0] = 'Empty'
                                tile_list[tile_menu[1]][1] = 0
                                color_list[tile_menu[1]] = BROWN
                                water -= 30
                                rock -= 30
                            else:
                                not_enough_resources.show()
                        elif tile_list[tile_menu[1]][0] == 'Sand':
                            if wood >= 30 and water >= 30:
                                rock += round(tile_list[tile_menu[1]][1])
                                tile_list[tile_menu[1]][0] = 'Empty'
                                tile_list[tile_menu[1]][1] = 0
                                color_list[tile_menu[1]] = BROWN
                                wood -= 30
                                water -= 30
                            else:
                                not_enough_resources.show()


                if build_button.click == True:
                    if tile_menu[0] == True:
                        if tile_list[tile_menu[1]][0] == 'Empty':
                            if rock >= 35 and wood >= 50:
                                max_population += 5
                                tile_list[tile_menu[1]][0] = 'Habitat'
                                color_list[tile_menu[1]] = DARK_BROWN
                                rock -= 35
                                wood -= 50
                            else:
                                not_enough_resources.show()

                if plant_button.click == True:
                    if tile_menu[0] == True:
                        if tile_list[tile_menu[1]][0] == 'Empty':
                            if wood >= 15 and water >= 5:
                                tile_list[tile_menu[1]][0] = 'Forest'
                                tile_list[tile_menu[1]][1] = randint(4, 100)
                                color_list[tile_menu[1]] = DARK_GREEN
                                wood -= 15
                                water -= 5
                            else:
                                not_enough_resources.show()

            if event.button == 4:
                if camera.distance >= min_distance:
                    camera.distance -= scroll_sensitivity
            if event.button == 5:
                if camera.distance <= max_distance:
                    camera.distance += scroll_sensitivity


    pressed = pygame.key.get_pressed()
    

    pressed = pygame.mouse.get_pressed()
    if pressed[2]:
        right_click = True
    else:
        right_click = False

    not_enough_resources.next_frame()
    cant_start_day.next_frame()


    pygame.display.update()

pygame.quit()
