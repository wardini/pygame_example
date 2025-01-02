import asyncio
import pygame
import sys
import random

window: pygame.Surface
clock: pygame.time.Clock = pygame.time.Clock()
fps: int = 60
fullscreen: bool = False
screensize: pygame.Vector2 = pygame.Vector2(800, 600)
PSIZE: int = 10  # size of player
TSIZE: int = 20  # size of target
MAXVEL: int = 2000  # max velocity of player

if len(sys.argv) > 1:
    fullscreen = sys.argv[1] == "full"

pygame.init()
if fullscreen:
    window = pygame.display.set_mode(
        screensize, flags=pygame.FULLSCREEN | pygame.SCALED
    )
else:
    window = pygame.display.set_mode(screensize)

pygame.display.set_caption("Dave's Example Game")


class Player:
    def __init__(self):
        self.acceleration: pygame.Vector2 = pygame.Vector2(0, 0)
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)
        self.position: pygame.Vector2 = screensize // 2

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.acceleration += pygame.Vector2(0, -1)
            elif event.key == pygame.K_DOWN:
                self.acceleration += pygame.Vector2(0, 1)
            elif event.key == pygame.K_LEFT:
                self.acceleration += pygame.Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.acceleration += pygame.Vector2(1, 0)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.acceleration -= pygame.Vector2(0, -1)
            elif event.key == pygame.K_DOWN:
                self.acceleration -= pygame.Vector2(0, 1)
            elif event.key == pygame.K_LEFT:
                self.acceleration -= pygame.Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.acceleration -= pygame.Vector2(1, 0)

    def update(self, dt):
        self.velocity += dt * self.acceleration / 10
        if self.velocity.magnitude() > 0:
            if self.velocity.magnitude() > MAXVEL:
                self.velocity = self.velocity.normalize() * MAXVEL
        self.position += dt * self.velocity / 1000
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity.reflect_ip(pygame.Vector2(1, 0))
        elif self.position[0] > screensize[0] - PSIZE:
            self.position[0] = screensize[0] - PSIZE
            self.velocity.reflect_ip(pygame.Vector2(-1, 0))

        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity.reflect_ip(pygame.Vector2(0, 1))
        elif self.position[1] > screensize[1] - PSIZE:
            self.position[1] = screensize[1] - PSIZE
            self.velocity.reflect_ip(pygame.Vector2(0, -1))
        self.rect = pygame.Rect(*self.position, PSIZE, PSIZE)

    def draw(self, window):
        pygame.draw.rect(window, pygame.Color("green"), self.rect)


class Target:
    def __init__(self):
        self.alive = True
        self.place_target()

    def place_target(self):
        x = random.randint(TSIZE, int(screensize[0]) - TSIZE)
        y = random.randint(TSIZE, int(screensize[1]) - TSIZE)
        self.position = pygame.Vector2(x, y)

    def process_event(self, event):
        pass

    def update(self, dt):
        self.rect = pygame.Rect(*self.position, TSIZE, TSIZE)

    def draw(self, window):
        pygame.draw.rect(window, pygame.Color("red"), self.rect)


class Score:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont("default", 80)
        self.position = pygame.Vector2(screensize[0] // 2, 50)

    def increment(self):
        self.score += 1

    def update(self, dt):
        self.text_surface = self.font.render(
            f"{self.score:05d}", True, pygame.Color("yellow")
        )
        self.rect = self.text_surface.get_rect(center=(self.position))

    def draw(self, window):
        window.blit(self.text_surface, self.rect)


class Game:
    def __init__(self):
        self.done: bool = False
        self.player = Player()
        self.target = Target()
        self.score = Score()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            else:
                self.player.process_event(event)

    def update(self, dt):
        self.player.update(dt)
        self.target.update(dt)

        if self.player.rect.colliderect(self.target.rect):
            self.score.increment()
            self.target.place_target()

        self.score.update(dt)

    def draw(self, window):
        window.fill(pygame.Color("black"))
        self.player.draw(window)
        self.target.draw(window)
        self.score.draw(window)

    async def run(self):
        while not self.done:
            dt = clock.tick(fps)
            self.event_loop()
            self.update(dt)
            self.draw(window)
            pygame.display.update()
            await asyncio.sleep(0)
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(Game().run())
