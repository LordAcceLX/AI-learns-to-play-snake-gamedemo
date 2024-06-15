import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('AlexBrush.ttf', 40)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
RED = (200, 0, 0)
YELLOW1 = (255, 255, 153)
YELLOW2 = (255, 255, 0)
BLACK = (0, 0, 0)

BLOCK = 20
SPEED = 20


class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK, self.head.y),
                      Point(self.head.x - (2 * BLOCK), self.head.y)]

        self.score = 0
        self.apple = None
        self._place_apple()
        self.frame_iteration = 0

    def _place_apple(self):
        x = random.randint(0, (self.w - BLOCK) // BLOCK) * BLOCK
        y = random.randint(0, (self.h - BLOCK) // BLOCK) * BLOCK
        self.apple = Point(x, y)
        if self.apple in self.snake:
            self._place_apple()

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 80 * len(self.snake):
            game_over = True
            reward = -20
            return reward, game_over, self.score

        if self.head == self.apple:
            self.score += 1
            reward = 10
            self._place_apple()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK or pt.x < 0 or pt.y > self.h - BLOCK or pt.y < 0:
            return True

        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, YELLOW1, pygame.Rect(pt.x, pt.y, BLOCK, BLOCK))
            pygame.draw.rect(self.display, YELLOW2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.apple.x, self.apple.y, BLOCK, BLOCK))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK
        elif self.direction == Direction.LEFT:
            x -= BLOCK
        elif self.direction == Direction.DOWN:
            y += BLOCK
        elif self.direction == Direction.UP:
            y -= BLOCK

        self.head = Point(x, y)