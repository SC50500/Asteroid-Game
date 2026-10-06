import pygame
import random
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60

NUM_ASTEROIDS = 5

ROTATION_SPEED = 3

THRUST = 0.15
DRAG = 0.99
MAX_SPEED = 7

MISSILE_SPEED = 8

BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
GREEN = (80, 255, 150)
YELLOW = (255, 230, 80)
RED = (255, 80, 80)
BLUE = (80, 180, 255)
ORANGE = (255, 140, 50)

FOV_THRESHOLD = 0.7
DETECTION_RANGE = 25

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(
    "Lesson 4 - Velocity, Acceleration, Momentum, and Drag"
)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)

class Spaceship:

    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.angle = 90
        self.radius = 18
        self.is_thrusting = False
        self.lives = 3

    def get_forward_vector(self):

        radians = math.radians(self.angle)

        forward = pygame.Vector2(
            math.cos(radians),
            -math.sin(radians)
        )

        return forward

    def update(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += ROTATION_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= ROTATION_SPEED

        forward = self.get_forward_vector()

        self.acceleration = pygame.Vector2(0, 0)

        self.is_thrusting = False

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.acceleration = forward * THRUST
            self.is_thrusting = True

        self.velocity += self.acceleration

        self.velocity *= DRAG

        if self.velocity.length() > MAX_SPEED:

            self.velocity.scale_to_length(MAX_SPEED)

        self.position += self.velocity

        if self.position.x > WIDTH:
            self.position.x = 0

        if self.position.x < 0:
            self.position.x = WIDTH

        if self.position.y > HEIGHT:
            self.position.y = 0

        if self.position.y < 0:
            self.position.y = HEIGHT

    def draw(self):

        forward = self.get_forward_vector()

        left = forward.rotate(140)
        right = forward.rotate(-140)

        front = self.position + forward * 22
        back_left = self.position + left * 17
        back_right = self.position + right * 17

        pygame.draw.polygon(
            screen,
            GREEN,
            [front, back_left, back_right],
            2
        )

        pygame.draw.circle(
            screen,
            GREEN,
            (int(self.position.x), int(self.position.y)),
            3
        )

        if self.is_thrusting:

            flame_position = (
                self.position - forward * 20
            )

            pygame.draw.circle(
                screen,
                ORANGE,
                (
                    int(flame_position.x),
                    int(flame_position.y)
                ),
                5
            )

    def draw_forward_vector(self):

        forward = self.get_forward_vector()

        end_point = (
            self.position + forward * 60
        )

        pygame.draw.line(
            screen,
            RED,
            self.position,
            end_point,
            2
        )

    def draw_velocity_vector(self):

        if self.velocity.length() > 0.1:

            end_point = (
                self.position
                + self.velocity * 10
            )

            pygame.draw.line(
                screen,
                BLUE,
                self.position,
                end_point,
                3
            )

class Asteroid:

    def __init__(self):

        self.radius = random.randint(18, 35)

        self.position = pygame.Vector2(
            random.randint(
                self.radius,
                WIDTH - self.radius
            ),
            random.randint(
                self.radius,
                HEIGHT - self.radius
            )
        )

        angle = random.uniform(
            0,
            2 * math.pi
        )

        speed = random.uniform(
            1.0,
            2.5
        )

        self.velocity = pygame.Vector2(
            math.cos(angle),
            math.sin(angle)
        ) * speed


    def update(self):

        self.position += self.velocity

        if self.position.x > WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.x < -self.radius:
            self.position.x = WIDTH + self.radius

        if self.position.y > HEIGHT + self.radius:
            self.position.y = -self.radius

        if self.position.y < -self.radius:
            self.position.y = HEIGHT + self.radius


    def draw(self):

        pygame.draw.circle(
            screen,
            GRAY,
            (
                int(self.position.x),
                int(self.position.y)
            ),
            self.radius,
            2
        )

class Missile:

    def __init__(self, start_position, direction):

        self.position = pygame.Vector2(
            start_position
        )

        self.radius = 4

        self.velocity = (
            direction * MISSILE_SPEED
        )


    def update(self):

        self.position += self.velocity


    def draw(self):

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                int(self.position.x),
                int(self.position.y)
            ),
            self.radius
        )


    def is_off_screen(self):

        return (
            self.position.x < 0
            or self.position.x > WIDTH
            or self.position.y < 0
            or self.position.y > HEIGHT
        )

def missile_hits_asteroid(
    missile,
    asteroid
):

    distance = (
        missile.position.distance_to(
            asteroid.position
        )
    )

    return (
        distance
        < missile.radius + asteroid.radius
    )

player = Spaceship(
    WIDTH / 2,
    HEIGHT / 2
)

enemy = Spaceship(
    700,
    300
)

enemy_angle = random.randint(0, 360)
enemy.angle = enemy_angle
detected = False

def enemy_attack():
    detected = True

asteroids = []

for i in range(NUM_ASTEROIDS):
    asteroids.append(
        Asteroid()
    )

missiles = []

score = 0

def asteroid_hits_ship(
    spaceship,
    asteroid
):
    distance = (
        asteroid.position.distance_to(
            spaceship.position
        )
    )

    return(
        distance < asteroid.radius + spaceship.radius
    )

running = True

while running:

    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        # -------------------------------------------------
        # Fire Missile
        # -------------------------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                # Missile fires in the direction
                # the spaceship is facing.
                forward = (
                    player.get_forward_vector()
                )

                missile_start = (
                    player.position
                    + forward * 24
                )

                new_missile = Missile(
                    missile_start,
                    forward
                )

                missiles.append(
                    new_missile
                )

    # =====================================================
    # 2. UPDATE PLAYER
    # =====================================================

    player.update()


    # =====================================================
    # 3. UPDATE ASTEROIDS
    # =====================================================

    for asteroid in asteroids:
        asteroid.update()


    # =====================================================
    # 4. UPDATE MISSILES
    # =====================================================

    for missile in missiles:
        missile.update()


    # =====================================================
    # 5. REMOVE OFF-SCREEN MISSILES
    # =====================================================

    missiles = [
        missile
        for missile in missiles
        if not missile.is_off_screen()
    ]


    # =====================================================
    # 6. MISSILE / ASTEROID COLLISION
    # =====================================================

    for missile in missiles[:]:

        for asteroid in asteroids[:]:

            if missile_hits_asteroid(
                missile,
                asteroid
            ):

                if missile in missiles:
                    missiles.remove(
                        missile
                    )

                if asteroid in asteroids:
                    asteroids.remove(
                        asteroid
                    )

                # Replace destroyed asteroid
                asteroids.append(
                    Asteroid()
                )

                score += 1

                break

    for asteroid in asteroids[:]:
        if asteroid_hits_ship(
            player,
            asteroid
        ):
            asteroids.remove(asteroid)
            player.lives -= 1

    forward = enemy.get_forward_vector()

    to_player = (
        player.position - enemy.position
    ).normalize()

    distance = player.position.distance_to(enemy.position)

    dot = forward.dot(to_player)

    if dot > FOV_THRESHOLD and distance < DETECTION_RANGE:
        enemy_attack()
        detected = True

    # =====================================================
    # 7. DRAW EVERYTHING
    # =====================================================

    screen.fill(BLACK)


    # Draw asteroids
    for asteroid in asteroids:
        asteroid.draw()


    # Draw missiles
    for missile in missiles:
        missile.draw()


    # -----------------------------------------------------
    # Draw vectors BEFORE ship
    # -----------------------------------------------------

    # RED = where ship is facing
    player.draw_forward_vector()

    # BLUE = where ship is actually moving
    player.draw_velocity_vector()


    # Draw spaceship
    player.draw()
    enemy.draw()

    # =====================================================
    # 8. DISPLAY INFORMATION
    # =====================================================

    forward = (
        player.get_forward_vector()
    )

    speed = (
        player.velocity.length()
    )


    # -----------------------------------------------------
    # Controls
    # -----------------------------------------------------

    controls_text = font.render(
        "LEFT/RIGHT: Rotate   UP: Thrust   SPACE: Fire",
        True,
        WHITE
    )

    screen.blit(
        controls_text,
        (20, 15)
    )

    # -----------------------------------------------------
    # Angle
    # -----------------------------------------------------

    angle_text = font.render(
        f"Angle: {player.angle % 360:.0f} degrees",
        True,
        WHITE
    )

    screen.blit(
        angle_text,
        (20, 45)
    )


    # -----------------------------------------------------
    # Forward Vector
    # -----------------------------------------------------

    forward_text = font.render(
        f"Forward: ({forward.x:.2f}, {forward.y:.2f})",
        True,
        RED
    )

    screen.blit(
        forward_text,
        (20, 75)
    )


    # -----------------------------------------------------
    # Velocity Vector
    # -----------------------------------------------------

    velocity_text = font.render(
        f"Velocity: ({player.velocity.x:.2f}, "
        f"{player.velocity.y:.2f})",
        True,
        BLUE
    )

    screen.blit(
        velocity_text,
        (20, 105)
    )


    # -----------------------------------------------------
    # Speed
    # -----------------------------------------------------

    speed_text = font.render(
        f"Speed: {speed:.2f}",
        True,
        WHITE
    )

    screen.blit(
        speed_text,
        (20, 135)
    )


    # -----------------------------------------------------
    # Acceleration
    # -----------------------------------------------------

    acceleration_text = font.render(
        f"Acceleration: "
        f"({player.acceleration.x:.2f}, "
        f"{player.acceleration.y:.2f})",
        True,
        WHITE
    )

    screen.blit(
        acceleration_text,
        (20, 165)
    )


    # -----------------------------------------------------
    # Score
    # -----------------------------------------------------

    score_text = font.render(
        f"Asteroids Hit: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (20, 195)
    )


    # -----------------------------------------------------
    # Vector Legend
    # -----------------------------------------------------

    legend_text = font.render(
        "RED = Facing Direction     BLUE = Velocity",
        True,
        WHITE
    )

    screen.blit(
        legend_text,
        (20, HEIGHT - 65)
    )

    lives_text = font.render(
        f"Lives Remaining: {player.lives}",
        True,
        WHITE
    )

    screen.blit(
        lives_text,
        (20, HEIGHT - 85)
    )

    enemy_text = font.render(
        f"Enemy State: {detected}",
        True,
        WHITE
    )

    screen.blit(
        enemy_text,
        (20, HEIGHT - 105)
    )

    # -----------------------------------------------------
    # Main Lesson Formula
    # -----------------------------------------------------

    formula_text = font.render(
        "Acceleration -> Velocity -> Position",
        True,
        GREEN
    )

    screen.blit(
        formula_text,
        (20, HEIGHT - 35)
    )

    if player.lives <= 0:
        pygame.quit()

    pygame.display.flip()


pygame.quit()