"""
3D Tank Game - Main Game File
Features: Player tank, AI enemies, physics, collision, health system
"""

from ursina import *
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
game_score = 0
game_level = 1
enemies_defeated = 0
enemies_list = []
projectiles_list = []

# ============= UTILITY FUNCTIONS =============
def calc_distance(pos1, pos2):
    """Calculate distance between two 3D positions"""
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    dz = pos1[2] - pos2[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def get_delta_time():
    """Get delta time safely"""
    try:
        return globals()['dt'] if 'dt' in globals() else 0.016
    except:
        return 0.016

# ============= TANK CLASS =============
class Tank(Entity):
    def __init__(self, x, z, is_player_tank=False, tank_color=color.blue):
        super().__init__()
        self.position = (x, 0.5, z)
        self.scale = (1.5, 1, 2)
        self.model = 'cube'
        self.color = tank_color
        self.is_player_tank = is_player_tank
        
        # Tank properties
        self.tank_health = PLAYER_HEALTH if is_player_tank else ENEMY_HEALTH
        self.tank_max_health = self.tank_health
        self.tank_velocity = Vec3(0, 0, 0)
        self.tank_rotation = 0
        self.tank_shoot_timer = 0.0
        self.tank_speed = PLAYER_SPEED if is_player_tank else ENEMY_SPEED
        
        # Turret
        self.gun_turret = Entity(
            parent=self,
            model='cube',
            scale=(0.4, 0.4, 1.2),
            position=(0, 0.7, 0),
            color=tank_color
        )
        
        # Health bar background
        self.hb_background = Entity(
            parent=self,
            model='quad',
            scale=(1.5, 0.1, 1),
            position=(0, 2, 0),
            color=color.gray
        )
        self.hb_fill = Entity(
            parent=self.hb_background,
            model='quad',
            scale=(1, 1, 1),
            position=(0, 0, 0.01),
            color=color.green
        )
    
    def update_health_visual(self):
        ratio = max(0, self.tank_health / self.tank_max_health)
        self.hb_fill.scale_x = ratio
        self.hb_fill.x = (ratio - 1) * 0.75
        
        if ratio > 0.5:
            self.hb_fill.color = color.green
        elif ratio > 0.25:
            self.hb_fill.color = color.yellow
        else:
            self.hb_fill.color = color.red
    
    def apply_damage(self, dmg):
        self.tank_health -= dmg
        self.update_health_visual()
        if self.tank_health <= 0:
            self.destroy_tank()
    
    def destroy_tank(self):
        destroy(self)
        destroy(self.gun_turret)
        destroy(self.hb_background)
    
    def fire_gun(self):
        if self.tank_shoot_timer <= 0:
            gun_pos = self.gun_turret.world_position
            gun_dir = self.get_gun_direction()
            new_proj = Projectile(gun_pos, gun_dir, owner_tank=self)
            projectiles_list.append(new_proj)
            self.tank_shoot_timer = 0.5
    
    def get_gun_direction(self):
        angle_rad = math.radians(self.tank_rotation)
        gun_direction = Vec3(math.sin(angle_rad), 0, math.cos(angle_rad))
        return gun_direction.normalized()

# ============= PROJECTILE CLASS =============
class Projectile(Entity):
    def __init__(self, start_pos, start_dir, owner_tank, proj_dmg=20):
        super().__init__()
        self.position = start_pos + start_dir * 2
        self.model = 'sphere'
        self.scale = 0.3
        self.color = color.yellow
        
        self.proj_velocity = start_dir * PROJECTILE_SPEED
        self.proj_owner = owner_tank
        self.proj_damage = proj_dmg
        self.proj_lifetime = 10.0
        self.proj_gravity = -20
    
    def update_projectile(self):
        dt = 0.016  # Fixed delta time
        self.proj_lifetime -= dt
        
        # Apply gravity
        self.proj_velocity.y += self.proj_gravity * dt
        
        # Update position
        self.position += self.proj_velocity * dt
        
        # Check collisions
        if self.proj_owner.is_player_tank:
            check_targets = enemies_list
        else:
            check_targets = [player_tank_obj]
        
        for target_tank in check_targets:
            dist = calc_distance(self.position, target_tank.position)
            if dist < 1.5:
                target_tank.apply_damage(self.proj_damage)
                destroy(self)
                return
        
        # Check bounds
        if abs(self.position.x) > GAME_WIDTH or abs(self.position.z) > GAME_HEIGHT or self.position.y < 0 or self.proj_lifetime < 0:
            destroy(self)

# ============= PLAYER TANK =============
player_tank_obj = Tank(0, 0, is_player_tank=True, tank_color=color.blue)

# ============= SPAWN ENEMIES =============
def spawn_enemy_wave():
    global enemies_list, game_level
    enemies_list = []
    num_spawned = 2 + game_level
    for _ in range(num_spawned):
        ex = random.uniform(-GAME_WIDTH/2 + 5, GAME_WIDTH/2 - 5)
        ez = random.uniform(-GAME_HEIGHT/2 + 5, GAME_HEIGHT/2 - 5)
        if calc_distance((ex, 0.5, ez), (0, 0.5, 0)) > 15:
            new_enemy = Tank(ex, ez, is_player_tank=False, tank_color=color.red)
            enemies_list.append(new_enemy)

spawn_enemy_wave()

# ============= INPUT & CONTROLS =============
def input(key):
    if key == 'w':
        direction = player_tank_obj.get_gun_direction()
        player_tank_obj.tank_velocity = direction * player_tank_obj.tank_speed
    elif key == 's':
        direction = player_tank_obj.get_gun_direction()
        player_tank_obj.tank_velocity = -direction * player_tank_obj.tank_speed
    elif key == 'a':
        player_tank_obj.tank_rotation += 5
    elif key == 'd':
        player_tank_obj.tank_rotation -= 5
    elif key == 'space':
        player_tank_obj.fire_gun()
    elif key == 'escape':
        application.quit()

# ============= MAIN UPDATE LOOP =============
def update_game():
    global game_score, game_level, enemies_defeated
    
    dt = 0.016  # Fixed delta time
    
    # Update player shoot timer
    player_tank_obj.tank_shoot_timer -= dt
    
    # Update player movement
    player_tank_obj.tank_velocity *= FRICTION
    player_tank_obj.position += player_tank_obj.tank_velocity * dt
    
    # Clamp player bounds
    player_tank_obj.position.x = clamp(player_tank_obj.position.x, -GAME_WIDTH/2, GAME_WIDTH/2)
    player_tank_obj.position.z = clamp(player_tank_obj.position.z, -GAME_HEIGHT/2, GAME_HEIGHT/2)
    
    # Update camera
    cam_distance = 15
    camera.position = player_tank_obj.position + Vec3(0, cam_distance, -cam_distance * 0.7)
    camera.look_at(player_tank_obj.position + Vec3(0, 2, 0))
    
    # Update enemies
    for enemy_tank in enemies_list[:]:
        if not enemy_tank:
            continue
        
        # AI movement
        direction_to_player = (player_tank_obj.position - enemy_tank.position).normalized()
        enemy_tank.tank_velocity = direction_to_player * enemy_tank.tank_speed
        enemy_tank.position += enemy_tank.tank_velocity * dt
        
        # Clamp bounds
        enemy_tank.position.x = clamp(enemy_tank.position.x, -GAME_WIDTH/2, GAME_WIDTH/2)
        enemy_tank.position.z = clamp(enemy_tank.position.z, -GAME_HEIGHT/2, GAME_HEIGHT/2)
        
        # AI shoot
        enemy_tank.tank_shoot_timer -= dt
        dist_to_player = calc_distance(enemy_tank.position, player_tank_obj.position)
        if dist_to_player < 30 and enemy_tank.tank_shoot_timer <= 0:
            direction = (player_tank_obj.position - enemy_tank.position).normalized()
            enemy_tank.gun_turret.rotation = (0, math.degrees(math.atan2(direction.x, direction.z)), 0)
            enemy_tank.fire_gun()
        
        # Remove dead enemies
        if enemy_tank.tank_health <= 0:
            enemies_list.remove(enemy_tank)
            enemies_defeated += 1
            game_score += 10
    
    # Update projectiles
    for proj in projectiles_list[:]:
        if proj:
            proj.update_projectile()
        else:
            if proj in projectiles_list:
                projectiles_list.remove(proj)
    
    # Check level
    if len(enemies_list) == 0 and enemies_defeated > 0:
        game_level += 1
        spawn_enemy_wave()
    
    # Check game over
    if player_tank_obj.tank_health <= 0:
        print("GAME OVER! Final Score: {}, Level: {}".format(game_score, game_level))
        application.quit()

# ============= UI =============
txt_score = Text(text='Score: 0', position=(-0.9, 0.45), scale=2)
txt_health = Text(text='Health: 100', position=(-0.9, 0.4), scale=2)
txt_level = Text(text='Level: 1', position=(-0.9, 0.35), scale=2)
txt_controls = Text(text='W/A/S/D: Move | SPACE: Shoot | ESC: Quit', position=(-0.9, -0.45), scale=1.5)

def update_ui_display():
    txt_score.text = 'Score: {}'.format(game_score)
    txt_health.text = 'Health: {}'.format(max(0, int(player_tank_obj.tank_health)))
    txt_level.text = 'Level: {} | Enemies: {}'.format(game_level, len(enemies_list))

# Add ground
ground_entity = Entity(
    model='cube',
    scale=(GAME_WIDTH, 0.1, GAME_HEIGHT),
    position=(0, -0.5, 0),
    color=color.light_gray,
    collider='box'
)

# Add walls
for wall_x in [-GAME_WIDTH/2, GAME_WIDTH/2]:
    Entity(model='cube', scale=(1, 2, GAME_HEIGHT), position=(wall_x, 1, 0), color=color.green, collider='box')
for wall_z in [-GAME_HEIGHT/2, GAME_HEIGHT/2]:
    Entity(model='cube', scale=(GAME_WIDTH, 2, 1), position=(0, 1, wall_z), color=color.green, collider='box')

# Add obstacles
for _ in range(5):
    obs_x = random.uniform(-GAME_WIDTH/2 + 5, GAME_WIDTH/2 - 5)
    obs_z = random.uniform(-GAME_HEIGHT/2 + 5, GAME_HEIGHT/2 - 5)
    Entity(model='cube', scale=(2, 1.5, 2), position=(obs_x, 0.75, obs_z), color=color.gray, collider='box')

# Game loop
while True:
    update_game()
    update_ui_display()
