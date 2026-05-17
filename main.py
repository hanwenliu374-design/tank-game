"""
3D Tank Game - Main Game File
Features: Player tank, AI enemies, physics, collision, health system
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# Initialize game
app = Ursina(title="Tank Battle 3D")
camera.position = (0, 15, -20)
camera.rotation = (45, 0, 0)

# Game Settings
GAME_WIDTH = 100
GAME_HEIGHT = 100
PLAYER_SPEED = 30
PLAYER_HEALTH = 100
ENEMY_SPEED = 15
ENEMY_HEALTH = 50
PROJECTILE_SPEED = 60
FRICTION = 0.95

# Game State
player_health = PLAYER_HEALTH
enemies = []
projectiles = []
score = 0
level = 1
enemies_defeated = 0

# ============= UTILITY FUNCTIONS =============
def distance_between(pos1, pos2):
    """Calculate distance between two 3D positions"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)

# ============= TANK CLASS =============
class Tank(Entity):
    def __init__(self, x, z, is_player=False, tank_color=color.blue):
        super().__init__()
        self.position = (x, 0.5, z)
        self.scale = (1.5, 1, 2)
        self.model = 'cube'
        self.color = tank_color
        self.is_player = is_player
        
        # Tank properties
        self.health = PLAYER_HEALTH if is_player else ENEMY_HEALTH
        self.max_health = self.health
        self.velocity = Vec3(0, 0, 0)
        self.rotation_y = 0
        self.shoot_timer = 0.0
        self.speed = PLAYER_SPEED if is_player else ENEMY_SPEED
        
        # Turret
        self.turret = Entity(
            parent=self,
            model='cube',
            scale=(0.4, 0.4, 1.2),
            position=(0, 0.7, 0),
            color=tank_color
        )
        
        # Health bar background
        self.health_bar_bg = Entity(
            parent=self,
            model='quad',
            scale=(1.5, 0.1, 1),
            position=(0, 2, 0),
            color=color.gray
        )
        self.health_bar = Entity(
            parent=self.health_bar_bg,
            model='quad',
            scale=(1, 1, 1),
            position=(0, 0, 0.01),
            color=color.green
        )
    
    def update_health_bar(self):
        health_ratio = max(0, self.health / self.max_health)
        self.health_bar.scale_x = health_ratio
        self.health_bar.x = (health_ratio - 1) * 0.75
        
        if health_ratio > 0.5:
            self.health_bar.color = color.green
        elif health_ratio > 0.25:
            self.health_bar.color = color.yellow
        else:
            self.health_bar.color = color.red
    
    def take_damage(self, damage):
        self.health -= damage
        self.update_health_bar()
        if self.health <= 0:
            self.die()
    
    def die(self):
        destroy(self)
        destroy(self.turret)
        destroy(self.health_bar_bg)
    
    def shoot(self):
        if self.shoot_timer <= 0:
            turret_world_pos = self.turret.world_position
            direction = self.get_turret_direction()
            projectile = Projectile(turret_world_pos, direction, owner=self)
            projectiles.append(projectile)
            self.shoot_timer = 0.5
    
    def get_turret_direction(self):
        # Calculate direction based on tank rotation and turret angle
        angle_rad = math.radians(self.rotation_y)
        direction = Vec3(math.sin(angle_rad), 0, math.cos(angle_rad))
        return direction.normalized()

# ============= PROJECTILE CLASS =============
class Projectile(Entity):
    def __init__(self, pos, direction, owner, damage=20):
        super().__init__()
        self.position = pos + direction * 2
        self.model = 'sphere'
        self.scale = 0.3
        self.color = color.yellow
        
        self.velocity = direction * PROJECTILE_SPEED
        self.owner = owner
        self.damage = damage
        self.lifetime = 10
        self.gravity = -20
    
    def update(self):
        self.lifetime -= time.dt()
        
        # Apply gravity
        self.velocity.y += self.gravity * time.dt()
        
        # Update position
        self.position += self.velocity * time.dt()
        
        # Check collisions with tanks
        for tank in enemies if self.owner.is_player else [player_tank]:
            dist = distance_between(self.position, tank.position)
            if dist < 1.5:
                tank.take_damage(self.damage)
                destroy(self)
                return
        
        # Check world bounds
        if abs(self.position.x) > GAME_WIDTH or abs(self.position.z) > GAME_HEIGHT or self.position.y < 0 or self.lifetime < 0:
            destroy(self)

# ============= PLAYER TANK =============
player_tank = Tank(0, 0, is_player=True, tank_color=color.blue)

# ============= SPAWN ENEMIES =============
def spawn_enemies():
    global enemies
    enemies = []
    num_enemies = 2 + level
    for _ in range(num_enemies):
        x = random.uniform(-GAME_WIDTH/2 + 5, GAME_WIDTH/2 - 5)
        z = random.uniform(-GAME_HEIGHT/2 + 5, GAME_HEIGHT/2 - 5)
        if distance_between((x, 0.5, z), (0, 0.5, 0)) > 15:
            enemy = Tank(x, z, is_player=False, tank_color=color.red)
            enemies.append(enemy)

spawn_enemies()

# ============= INPUT & CONTROLS =============
def input(key):
    global score
    if key == 'w':
        direction = player_tank.get_turret_direction()
        player_tank.velocity = direction * player_tank.speed
    elif key == 's':
        direction = player_tank.get_turret_direction()
        player_tank.velocity = -direction * player_tank.speed
    elif key == 'a':
        player_tank.rotation_y += 5
    elif key == 'd':
        player_tank.rotation_y -= 5
    elif key == 'space':
        player_tank.shoot()
    elif key == 'escape':
        application.quit()

# ============= MAIN UPDATE LOOP =============
def update():
    global player_health, score, level, enemies_defeated
    
    # Update player shoot timer
    player_tank.shoot_timer -= time.dt()
    
    # Update player movement (friction)
    player_tank.velocity *= FRICTION
    player_tank.position += player_tank.velocity * time.dt()
    
    # Clamp player to world bounds
    player_tank.position.x = clamp(player_tank.position.x, -GAME_WIDTH/2, GAME_WIDTH/2)
    player_tank.position.z = clamp(player_tank.position.z, -GAME_HEIGHT/2, GAME_HEIGHT/2)
    
    # Update camera to follow player
    camera_distance = 15
    camera.position = player_tank.position + Vec3(0, camera_distance, -camera_distance * 0.7)
    camera.look_at(player_tank.position + Vec3(0, 2, 0))
    
    # Update enemies
    for enemy in enemies[:]:
        if not enemy:
            continue
        
        # AI: Move towards player
        direction_to_player = (player_tank.position - enemy.position).normalized()
        enemy.velocity = direction_to_player * enemy.speed
        enemy.position += enemy.velocity * time.dt()
        
        # Clamp to world bounds
        enemy.position.x = clamp(enemy.position.x, -GAME_WIDTH/2, GAME_WIDTH/2)
        enemy.position.z = clamp(enemy.position.z, -GAME_HEIGHT/2, GAME_HEIGHT/2)
        
        # AI: Shoot at player occasionally
        enemy.shoot_timer -= time.dt()
        dist_to_player = distance_between(enemy.position, player_tank.position)
        if dist_to_player < 30 and enemy.shoot_timer <= 0:
            direction = (player_tank.position - enemy.position).normalized()
            enemy.turret.rotation = (0, math.degrees(math.atan2(direction.x, direction.z)), 0)
            enemy.shoot()
        
        # Remove dead enemies
        if enemy.health <= 0:
            enemies.remove(enemy)
            enemies_defeated += 1
            score += 10
    
    # Update projectiles
    for projectile in projectiles[:]:
        if projectile:
            projectile.update()
        else:
            if projectile in projectiles:
                projectiles.remove(projectile)
    
    # Check level completion
    if len(enemies) == 0 and enemies_defeated > 0:
        level += 1
        spawn_enemies()
    
    # Check game over
    if player_tank.health <= 0:
        print(f"GAME OVER! Final Score: {score}, Level: {level}")
        application.quit()

# ============= UI =============
score_text = Text(text=f'Score: {score}', position=(-0.9, 0.45), scale=2)
health_text = Text(text=f'Health: {player_tank.health}', position=(-0.9, 0.4), scale=2)
level_text = Text(text=f'Level: {level}', position=(-0.9, 0.35), scale=2)
controls_text = Text(text='W/A/S/D: Move | SPACE: Shoot | ESC: Quit', position=(-0.9, -0.45), scale=1.5)

def update_ui():
    score_text.text = f'Score: {score}'
    health_text.text = f'Health: {max(0, int(player_tank.health))}'
    level_text.text = f'Level: {level} | Enemies: {len(enemies)}'

# Add ground
ground = Entity(
    model='cube',
    scale=(GAME_WIDTH, 0.1, GAME_HEIGHT),
    position=(0, -0.5, 0),
    color=color.light_gray,
    collider='box'
)

# Add walls
for x in [-GAME_WIDTH/2, GAME_WIDTH/2]:
    Entity(model='cube', scale=(1, 2, GAME_HEIGHT), position=(x, 1, 0), color=color.green, collider='box')
for z in [-GAME_HEIGHT/2, GAME_HEIGHT/2]:
    Entity(model='cube', scale=(GAME_WIDTH, 2, 1), position=(0, 1, z), color=color.green, collider='box')

# Add decorative obstacles
for _ in range(5):
    x = random.uniform(-GAME_WIDTH/2 + 5, GAME_WIDTH/2 - 5)
    z = random.uniform(-GAME_HEIGHT/2 + 5, GAME_HEIGHT/2 - 5)
    Entity(model='cube', scale=(2, 1.5, 2), position=(x, 0.75, z), color=color.gray, collider='box')

# Game loop
while True:
    update()
    update_ui()
