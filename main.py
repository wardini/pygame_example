import asyncio
import pygame
import random

SCREENSIZE: pygame.Vector2 = pygame.Vector2(800, 600)
FPS: int = 60  # frame rate if frames per second
PSIZE: int = 10  # size of player in pixels
TSIZE: int = 20  # size of target in pixels
PMASS: float = 10000.0 # mass of player (arbitrary units)
MAXVEL: float = 0.5  # max velocity of player pixels / millisecond

class Player:
    def __init__(self):
        self.force: pygame.Vector2 = pygame.Vector2(0, 0)
        self.acceleration: pygame.Vector2 = pygame.Vector2(0, 0)
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)
        self.position: pygame.Vector2 = SCREENSIZE // 2

    def process_event(self, event):
        if event.type in [pygame.KEYDOWN,pygame.KEYUP]:
            keys = pygame.key.get_pressed()
            self.force[0] = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            self.force[1] = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

    def update(self, dt):
        # perform physics
        self.acceleration = self.force / PMASS
        self.velocity += dt * self.acceleration
        if self.velocity.magnitude() > MAXVEL:
            self.velocity = self.velocity.normalize() * MAXVEL
        self.position += dt * self.velocity

        # restrict horizontal position to screen bounds
        # and bounce off walls
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity.reflect_ip(pygame.Vector2(1, 0))
        elif self.position[0] > SCREENSIZE[0] - PSIZE:
            self.position[0] = SCREENSIZE[0] - PSIZE
            self.velocity.reflect_ip(pygame.Vector2(-1, 0))

        # restrict vertical position to screen bounds
        # and bounce off walls
        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity.reflect_ip(pygame.Vector2(0, 1))
        elif self.position[1] > SCREENSIZE[1] - PSIZE:
            self.position[1] = SCREENSIZE[1] - PSIZE
            self.velocity.reflect_ip(pygame.Vector2(0, -1))

        # update player rectangle
        self.rect = pygame.Rect(*self.position, PSIZE, PSIZE)

    def draw(self, window):
        pygame.draw.rect(window, pygame.Color("green"), self.rect)


class Target:
    def __init__(self):
        self.alive = True
        self.place_target()

    def place_target(self):
        x = random.randint(TSIZE, int(SCREENSIZE[0]) - TSIZE)
        y = random.randint(TSIZE, int(SCREENSIZE[1]) - TSIZE)
        self.position = pygame.Vector2(x, y)

    def process_event(self, event):
        pass

    def update(self, dt):
        self.rect = pygame.Rect(*self.position, TSIZE, TSIZE)

    def draw(self, window):
        pygame.draw.rect(window, pygame.Color("red"), self.rect)


class GameInfo:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont(None, size=40)
        self.iposition = pygame.Vector2(SCREENSIZE[0] // 2, 20)
        self.sposition = pygame.Vector2(SCREENSIZE[0] // 2, 60)
        self.instructions = self.font.render("Move green square to collect red targets", True, pygame.Color("green"))
        self.irect = self.instructions.get_rect(center=self.iposition)

    def score_increment(self):
        self.score += 1

    def update(self, dt):
        self.text_surface = self.font.render(
            f"{self.score:05d}", True, pygame.Color("yellow")
        )
        self.rect = self.text_surface.get_rect(center=(self.sposition))

    def draw(self, window):
        window.blit(self.instructions, self.irect)
        window.blit(self.text_surface, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(SCREENSIZE)
        pygame.display.set_caption("Dave's Example Game")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.pickup_sound: pygame.mixer.Sound = pygame.mixer.Sound("audio/pickup.ogg")
        self.pickup_sound.set_volume(0.1)
        # self.miss_sound: pygame.mixer.Sound = pygame.mixer.Sound("audio/miss.ogg")
        # self.miss_sound.set_volume(0.2)
        self.done: bool = False
        self.player: Player = Player()
        self.target: Target = Target()
        self.gameinfo: GameInfo = GameInfo()

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
            self.gameinfo.score_increment()
            self.target.place_target()
            self.pickup_sound.play()

        self.gameinfo.update(dt)

    def draw(self, window):
        window.fill(pygame.Color("black"))
        self.player.draw(window)
        self.target.draw(window)
        self.gameinfo.draw(window)

    async def run(self):
        while not self.done:
            dt = self.clock.tick(FPS)
            self.event_loop()
            self.update(dt)
            self.draw(self.window)
            pygame.display.update()
            await asyncio.sleep(0)
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(Game().run())
