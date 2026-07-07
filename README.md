# 🤖 Automated Minesweeper Bot

A sophisticated constraint satisfaction solver that automates Minesweeper gameplay using advanced deduction techniques and real-time game integration.

## 🎯 Features

### Core Engine
- **Advanced Constraint Satisfaction** - Solves boards using logical deduction
- **Multiple Techniques**:
  - Basic Constraints (mine counting)
  - Naked Singles (cells with one possibility)
  - Hidden Singles (forced mine positions)
  - Pointing Pairs (mine elimination)
  - Advanced Constraints (X-Wing patterns)
  - Probability Analysis (statistical deduction)

### Game Integration
- **Selenium-based Automation** - Connects to minesweeperonline.com
- **Real-time Board Reading** - Extracts cell states from browser
- **Automated Click/Flag** - Executes moves with precision
- **Game State Tracking** - Monitors win/loss conditions

### Backend & Analytics
- **Express.js REST API** - Full game tracking
- **SQLite Database** - Persistent move history
- **Statistics Dashboard** - Performance metrics
- **Deduction Analysis** - Technique effectiveness tracking

---

## 📁 Project Structure

```
minesweeper-bot/
├── constraint_solver.py          # Pure logic engine
├── minesweeper_bot.py            # Bot controller
├── game_integration.py           # Game connection
├── auto_play.py                  # Main execution loop
├── dashboard.py                  # Real-time UI (optional)
├── requirements.txt              # Python dependencies
│
└── backend/
    ├── package.json              # Node dependencies
    ├── server.js                 # Express API server
    ├── database.js               # Database utilities
    └── data/
        └── minesweeper.db        # SQLite database (auto-generated)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Google Chrome/Chromium
- ChromeDriver ([download](https://chromedriver.chromium.org/))

### Setup

**1. Clone Repository**
```bash
git clone https://github.com/5q5hxmq5j5-cloud/Otfbot.git
cd Otfbot
```

**2. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

**3. Install Node Dependencies** (optional, for backend)
```bash
cd backend
npm install
```

**4. Download ChromeDriver**
```bash
# https://chromedriver.chromium.org/
# Place in PATH or project root
```

---

## 💻 Usage

### Run Bot Automatically
```bash
python auto_play.py
```

**Output:**
```
============================================================
AUTOMATED MINESWEEPER BOT
============================================================

🎮 Starting beginner Minesweeper game...
Platform: minesweeperonline
✓ Connected!
  Board: 8×8
  Mines: 10
  Difficulty: beginner

🤖 Bot is playing...

Move 1 [0.5s]: CLICK [3, 4]
  Technique: Basic Constraint (All mines found)
  Confidence: 100.0%

Move 2 [1.2s]: FLAG [5, 6]
  Technique: Hidden Single
  Confidence: 100.0%

🎉 GAME WON!

============================================================
GAME STATISTICS
============================================================
Total Moves: 45
Cells Clicked: 40
Cells Flagged: 10
Game Won: ✓
Game Lost: ✗
============================================================
```

### Run Backend Server
```bash
cd backend
npm start
```

Server runs on `http://localhost:5000`

---

## 📊 API Endpoints

### Games
- `POST /api/games` - Create new game
- `GET /api/games` - List all games (paginated)
- `GET /api/games/:game_id` - Get game details
- `PATCH /api/games/:game_id` - Update game status

### Moves
- `POST /api/games/:game_id/moves` - Record a move
- `GET /api/games/:game_id/moves` - Get all moves

### Deductions
- `POST /api/games/:game_id/deductions` - Record deduction
- `GET /api/games/:game_id/deductions/:move_number` - Get move deductions

### Statistics
- `GET /api/statistics` - Overall stats
- `GET /api/statistics/by-difficulty` - Stats by difficulty
- `GET /api/statistics/by-technique` - Stats by technique
- `GET /api/statistics/by-platform` - Stats by platform

---

## 🔍 Algorithm Details

### Constraint Satisfaction Approach

The bot uses iterative constraint propagation:

1. **Analyze Numbered Cells** - For each revealed number, count adjacent mines
2. **Apply Basic Rules** - If all mines found, remaining cells are safe
3. **Find Naked Singles** - Unknown cells with only one possibility
4. **Find Hidden Singles** - Positions where mines must be placed
5. **Calculate Probabilities** - For cells with multiple possibilities
6. **Repeat** - Until no new deductions found or move is made

### Example Deduction

```
Board state:
  1 □ □
  □ □ □
  □ □ □

Cell [0,0] = 1 means exactly 1 adjacent mine
Adjacent cells: [0,1], [1,0], [1,1]

If [1,0] and [1,1] are already flagged:
  → [0,1] must be SAFE (all mines found)

If only [1,0] is flagged:
  → One of [0,1] or [1,1] is a mine
  → Probability = 50% each
```

---

## 📈 Performance Metrics

The backend tracks:
- **Win Rate** - Games won / total games
- **Average Moves** - Mean moves per game
- **Technique Effectiveness** - Success rate by deduction technique
- **Difficulty Progression** - Performance by difficulty level

---

## 🛠️ Configuration

### Bot Settings

Edit `auto_play.py`:
```python
player = AutomatedMinesweeperPlayer(
    platform=GamePlatform.MINESWEEPERONLINE  # Change platform
)

player.start_game(
    difficulty='beginner'  # 'beginner', 'intermediate', 'expert'
)

player.play_game(
    max_moves=1000,    # Stop after N moves
    verbose=True       # Print each move
)
```

### Backend Configuration

Edit `backend/server.js`:
```javascript
const PORT = process.env.PORT || 5000;  // Change port
const dbPath = '...'  // Change database location
```

---

## 🐛 Troubleshooting

### ChromeDriver Issues
```bash
# Error: ChromeDriver not found
# Solution: Install webdriver-manager
pip install webdriver-manager

# Or manually download:
# https://chromedriver.chromium.org/
```

### Selenium Connection Failed
```bash
# Error: Failed to connect to game
# Solution: Ensure Chrome/Chromium is installed
# Update Selenium: pip install --upgrade selenium
```

### Database Locked
```bash
# Error: database is locked
# Solution: Kill existing process
# Restart backend: npm start
```

---

## 📝 Example: Custom Bot Usage

```python
from constraint_solver import ConstraintSatisfactionSolver
from minesweeper_bot import MinesweeperBot

# Create solver
solver = ConstraintSatisfactionSolver(width=8, height=8, total_mines=10)

# Set known cells
solver.set_cell(0, 0, 'revealed', 1)  # Revealed cell with 1 adjacent mine
solver.set_cell(1, 1, 'flagged')       # Flagged mine

# Solve
deductions = solver.solve()

for result in deductions:
    print(f"[{result.cell[0]}, {result.cell[1]}] is {result.cell_type.name}")
    print(f"  Technique: {result.technique}")
    print(f"  Confidence: {result.confidence * 100:.1f}%")
    print(f"  Reasoning: {result.reasoning}")
```

---

## 📊 Statistics Schema

### Games Table
```sql
id              TEXT PRIMARY KEY
game_id         TEXT UNIQUE
platform        TEXT (minesweeperonline, microsoft, etc)
difficulty      TEXT (beginner, intermediate, expert)
board_width     INTEGER
board_height    INTEGER
mines           INTEGER
status          TEXT (playing, won, lost)
moves           INTEGER
won             BOOLEAN
lost            BOOLEAN
start_time      DATETIME
end_time        DATETIME
created_at      DATETIME
```

### Moves Table
```sql
id              TEXT PRIMARY KEY
game_id         TEXT
move_number     INTEGER
x, y            INTEGER (coordinates)
action          TEXT (click, flag)
technique       TEXT (deduction technique used)
confidence      REAL (0.0 - 1.0)
reasoning       TEXT (explanation)
result          TEXT (pending, success, failure)
timestamp       DATETIME
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Support more online Minesweeper sites
- [ ] Add machine learning component
- [ ] Web-based dashboard UI
- [ ] Performance optimizations
- [ ] Advanced solving techniques

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🙏 Acknowledgments

- Minesweeper algorithm inspiration from constraint satisfaction problems
- Selenium for reliable browser automation
- Express.js and SQLite for robust data tracking

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation
3. Check existing issues on GitHub
4. Create new issue with detailed description

---

**Happy Minesweeping! 💣🤖**
