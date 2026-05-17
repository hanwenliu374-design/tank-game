# Tank Battle 3D

A 3D tank game built with Python using Ursina (Panda3D).

## Features
- 🎮 3D third-person tank control
- 🤖 AI enemy tanks with intelligent behavior
- 💥 Projectile physics and collision detection
- ❤️ Health system with visual health bars
- 📈 Progressive difficulty levels
- 🏆 Score tracking
- 🌍 Large game world with obstacles

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

1. **Clone or create project directory:**
```bash
mkdir tank-game
cd tank-game
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## How to Run

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| **W** | Move Forward |
| **S** | Move Backward |
| **A** | Turn Left |
| **D** | Turn Right |
| **SPACE** | Shoot |
| **ESC** | Quit Game |

## Gameplay

1. **Objective**: Defeat all enemy tanks to complete a level
2. **Difficulty**: Each level spawns more enemies
3. **Health**: Both player and enemies have health bars
4. **Score**: Get 10 points for each enemy defeated
5. **Obstacles**: Avoid or use obstacles for cover

## Game Mechanics

### Player Tank
- Controlled by the player with WASD keys
- Can shoot projectiles with SPACE
- Health displayed at top-left
- Camera follows from behind and above

### Enemy Tanks
- AI-controlled tanks spawn at random locations
- Chase and shoot at the player
- Difficulty increases with each level
- Drop obstacles in the arena

### Physics
- Projectiles affected by gravity
- Collision detection with tanks
- Friction on movement for realistic feel
- World boundaries prevent escape

## Tips

1. **Use obstacles for cover** - enemies can't shoot through walls
2. **Keep moving** - standing still makes you an easy target
3. **Manage distance** - close range means higher hit rate
4. **Watch health** - retreat if health is low
5. **Clear levels** - defeat all enemies to progress

## Future Enhancements

- [ ] Sound effects and music
- [ ] Power-ups (health, rapid fire)
- [ ] Different weapon types
- [ ] Multiplayer mode
- [ ] Level editor
- [ ] Boss fights
- [ ] Armor upgrades

## Troubleshooting

### "Module not found" error
- Ensure you're in the virtual environment
- Run `pip install -r requirements.txt` again

### Game runs slowly
- Reduce screen resolution
- Close other applications
- Check your GPU drivers

### Shooting doesn't work
- Make sure SPACE key is pressed
- Check cooldown between shots (0.5 seconds)

## License

This project is open source and available for personal and educational use.

## Author

Created with Python, Ursina, and Panda3D
