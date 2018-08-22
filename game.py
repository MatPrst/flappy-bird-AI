#!/usr/bin/env python

__author__= "Mathias Parisot"
__email__= "parisot.mathias.31@gmail.com"

import pygame, sys, random, os, neural_net, numpy, genetic
from pygame.locals import *

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

WHITE = (255, 255, 255)
BLACK = ( 0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

FPS = 30

BALL_X_INIT = 50
BALL_Y_INIT = int(WINDOW_HEIGHT / 2)
BALL_SIZE_INIT = 8
BALL_VELOCITY_INIT = 5
BALL_GRAVITY_INIT = 1
BALL_COLOR_INIT = RED
BALL_SCORE_INIT = 0

PIPE_SPACE_INIT = 100
PIPE_WIDTH_INIT = 10
PIPE_COLOR_INIT = WHITE
PIPE_SPEED_INIT = -2
PIPES_DISTANCE = 150

class Ball:
    def __init__(self):
        self.x = BALL_X_INIT
        self.y = BALL_Y_INIT
        self.size = BALL_SIZE_INIT
        self.velocity = BALL_VELOCITY_INIT
        self.gravity = BALL_GRAVITY_INIT
        self.color = BALL_COLOR_INIT
        self.score = BALL_SCORE_INIT
        self.fitness = 0
        self.dead = False

        self.brain = neural_net.Neural_Network(4, 4, 1)

    def draw(self, display_surf):
        if not self.dead:
            pygame.draw.circle(display_surf, self.color, (self.x, self.y), self.size, 0)

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

        if self.y >= WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT
            self.velocity = 0
        elif self.y <= 0:
            self.y = 0
            self.velocity = 0

        self.increase_score()

    def jump(self):
        self.velocity += - self.gravity * 12

    def position(self):
        return (self.x, self.y)

    def increase_score(self):
        self.score += 1

    def dies(self):
        self.dead = True

    def exist(self):
        return not self.dead

    def think(self, pipe):

        # input = [0, 0, 0, 0]
        # input[0] = self.y
        # input[1] = pipe.top_x
        # input[2] = pipe.top_height
        # input[3] = pipe.bottom_y
        input = numpy.matrix([[self.y / WINDOW_HEIGHT], [pipe.top_x / WINDOW_WIDTH], [pipe.top_height / WINDOW_HEIGHT], [pipe.bottom_y / WINDOW_HEIGHT]])
        # print(input)
        #
        # print(type(input))
        # print(self.brain.feedforward(input))
        output = numpy.asscalar(self.brain.feedforward(input))
        # print(output)
        return output > 0.92


class Pipe:
    def __init__(self):
        self.width_space = PIPE_SPACE_INIT
        self.y_space = random.randint(int(self.width_space / 2), WINDOW_HEIGHT - int(self.width_space / 2))
        self.width = PIPE_WIDTH_INIT
        self.color = PIPE_COLOR_INIT
        self.speed = PIPE_SPEED_INIT

        self.top_x = WINDOW_WIDTH
        self.top_y = 0
        self.top_height = self.y_space - int(self.width_space / 2)

        self.bottom_x = WINDOW_WIDTH
        self.bottom_y = self.y_space + int(self.width_space / 2)
        self.bottom_height = WINDOW_HEIGHT - self.y_space + int(self.width_space / 2)

    def draw(self, display_surf):
        pygame.draw.rect(display_surf, self.color, (self.top_x, self.top_y, self.width, self.top_height))
        pygame.draw.rect(display_surf, self.color, (self.bottom_x, self.bottom_y, self.width, self.bottom_height))

    def update(self):
        self.top_x += self.speed
        self.bottom_x += self.speed

    def x_position(self):
        return self.top_x

    def width_value(self):
        return self.width

    # return a tuple (width of the space, y position of the middle of the space)
    def space(self):
        return (self.width_space, self.y_space)

def main():

    global WINDOW_WIDTH, WINDOW_HEIGHT, FPS, PIPES_DISTANCE

    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 0)
    pygame.display.set_caption('Flapibird')

    fpsClock = pygame.time.Clock()

    # create the ball
    # jumper = Ball()

    jumpers = genetic.Population(100)

    # create pipes array and first pipe
    pipes = []
    pipes.append(Pipe())

    for i in range(5):
        # game loop
        # while True:
        while not all(jumper.dead for jumper in jumpers.population):

            # events loop
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                # elif (event.type == KEYDOWN and event.key == K_SPACE):
                #     jumper.jump()



            DISPLAYSURF.fill(BLACK)

            # if jumper.think():
            #     jumper.jump()
            #
            # jumper.update()
            # # jumper.draw(DISPLAYSURF)

            closest_pipe = 0
            distance_closest_pipe = WINDOW_WIDTH

            for pipe in pipes:
                pipe.update()
                pipe.draw(DISPLAYSURF)

                # remove the pipes not anymore in the frame
                if pipe.x_position() < 0:
                    pipes = pipes[1:]

                if -pipe.width_value() < pipe.x_position() - BALL_X_INIT < distance_closest_pipe:
                    closest_pipe = pipe
                    distance_closest_pipe = pipe.x_position() - BALL_X_INIT

            # print(closest_pipe)

            for i, jumper in enumerate(jumpers.population):
                if not jumper.dead:
                    jumper_position = jumper.position()

                    # closest_pipe = 0
                    # distance_closest_pipe = WINDOW_WIDTH
                    #
                    # for pipe in pipes:
                    #     pipe.update()
                    #     pipe.draw(DISPLAYSURF)
                    #
                    #     # remove the pipes not anymore in the frame
                    #     if pipe.x_position() < 0:
                    #         pipes = pipes[1:]
                    #
                    #     if 0 < pipe.x_position() - jumper_position[0] < distance_closest_pipe:
                    #         closest_pipe = pipe
                    #         distance_closest_pipe = pipe.x_position() - jumper_position[0]

                    think = jumper.think(closest_pipe)
                    if think:
                        jumper.jump()

                    jumper.update()
                    # jumper.draw(DISPLAYSURF)

                    # check if ball touches pipe
                    # print("\n")
                    # print("closest x1", closest_pipe.x_position())
                    # print("closest x2",closest_pipe.x_position() + closest_pipe.width_value())
                    # print("ball x", BALL_X_INIT)
                    if not (closest_pipe.x_position() < BALL_X_INIT < closest_pipe.x_position() + closest_pipe.width_value() \
                    and not (closest_pipe.space()[1] - int(closest_pipe.space()[0] / 2) < jumper_position[1]< closest_pipe.space()[1] + int(closest_pipe.space()[0] / 2))):
                        # print(i)
                        jumper.draw(DISPLAYSURF)
                    else:
                        # print("AHAHAH")
                        jumper.dies()
                    #     pygame.quit()
                    #     sys.exit()

                    jumper.draw(DISPLAYSURF)
                    # increase score
                    # if pipes[0].x_position() == BALL_X_INIT and jumper.exist():
                    #     jumper.increase_score()


            # jumpers.update()

            # create new pipe
            if pipes[-1].x_position() % PIPES_DISTANCE == 0:
                pipes.append(Pipe())

            pygame.display.update()
            fpsClock.tick(FPS)

    print("fitness")
    jumpers.fitness()
    for jumper in jumpers.population:
        print(jumper.fitness)

if __name__ == '__main__':
    main()
