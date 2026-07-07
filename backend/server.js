/**
 * Minesweeper Bot Backend Server
 * Express.js API with SQLite database
 * 
 * Endpoints:
 * - POST   /api/games                          Create new game
 * - GET    /api/games                          List all games
 * - GET    /api/games/:game_id                 Get game details
 * - PATCH  /api/games/:game_id                 Update game status
 * - POST   /api/games/:game_id/moves           Record a move
 * - GET    /api/games/:game_id/moves           Get game moves
 * - POST   /api/games/:game_id/deductions      Record deduction
 * - GET    /api/games/:game_id/deductions/:move_number  Get deductions
 * - GET    /api/statistics                     Overall statistics
 * - GET    /api/statistics/by-difficulty       Stats by difficulty
 * - GET    /api/statistics/by-technique        Stats by technique
 */

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Database setup
const dbDir = path.join(__dirname, 'data');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const dbPath = path.join(dbDir, 'minesweeper.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err);
  } else {
    console.log('✓ Connected to SQLite database');
    initializeDatabase();
  }
});

// Initialize database schema
function initializeDatabase() {
  db.serialize(() => {
    // Games table
    db.run(`
      CREATE TABLE IF NOT EXISTS games (
        id TEXT PRIMARY KEY,
        game_id TEXT UNIQUE,
        platform TEXT,
        difficulty TEXT,
        board_width INTEGER,
        board_height INTEGER,
        mines INTEGER,
        status TEXT,
        result TEXT,
        moves INTEGER DEFAULT 0,
        won BOOLEAN DEFAULT 0,
        lost BOOLEAN DEFAULT 0,
        start_time DATETIME,
        end_time DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Moves table
    db.run(`
      CREATE TABLE IF NOT EXISTS moves (
        id TEXT PRIMARY KEY,
        game_id TEXT,
        move_number INTEGER,
        x INTEGER,
        y INTEGER,
        action TEXT,
        technique TEXT,
        confidence REAL,
        reasoning TEXT,
        result TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
      )
    `);

    // Deductions table
    db.run(`
      CREATE TABLE IF NOT EXISTS deductions (
        id TEXT PRIMARY KEY,
        game_id TEXT,
        move_number INTEGER,
        x INTEGER,
        y INTEGER,
        cell_type TEXT,
        technique TEXT,
        confidence REAL,
        reasoning TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
      )
    `);

    // Statistics table
    db.run(`
      CREATE TABLE IF NOT EXISTS statistics (
        id TEXT PRIMARY KEY,
        total_games INTEGER,
        total_wins INTEGER,
        total_losses INTEGER,
        win_rate REAL,
        average_moves INTEGER,
        average_time INTEGER,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('✓ Database schema initialized');
  });
}

// ============== GAME ENDPOINTS ==============

// Create a new game
app.post('/api/games', (req, res) => {
  const { platform, difficulty, board_width, board_height, mines } = req.body;
  const game_id = uuidv4();
  const id = uuidv4();

  const query = `
    INSERT INTO games (id, game_id, platform, difficulty, board_width, board_height, mines, status, result, moves, won, lost, start_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;

  db.run(
    query,
    [id, game_id, platform, difficulty, board_width, board_height, mines, 'playing', 'pending', 0, 0, 0, new Date().toISOString()],
    function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json({ id, game_id, message: '✓ Game created successfully' });
      }
    }
  );
});

// Get game by ID
app.get('/api/games/:game_id', (req, res) => {
  const { game_id } = req.params;

  db.get('SELECT * FROM games WHERE game_id = ?', [game_id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'Game not found' });
    } else {
      res.json(row);
    }
  });
});

// Get all games (paginated)
app.get('/api/games', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 50, 100);
  const offset = parseInt(req.query.offset) || 0;

  db.all(
    'SELECT * FROM games ORDER BY created_at DESC LIMIT ? OFFSET ?',
    [limit, offset],
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json(rows);
      }
    }
  );
});

// Update game status
app.patch('/api/games/:game_id', (req, res) => {
  const { game_id } = req.params;
  const { status, result, moves, won, lost, end_time } = req.body;

  const query = `
    UPDATE games 
    SET status = ?, result = ?, moves = ?, won = ?, lost = ?, end_time = ?
    WHERE game_id = ?
  `;

  db.run(
    query,
    [status || 'playing', result || 'pending', moves || 0, won ? 1 : 0, lost ? 1 : 0, end_time || new Date().toISOString(), game_id],
    function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json({ message: '✓ Game updated' });
      }
    }
  );
});

// ============== MOVES ENDPOINTS ==============

// Record a move
app.post('/api/games/:game_id/moves', (req, res) => {
  const { game_id } = req.params;
  const { move_number, x, y, action, technique, confidence, reasoning, result } = req.body;
  const id = uuidv4();

  db.get('SELECT id FROM games WHERE game_id = ?', [game_id], (err, row) => {
    if (err || !row) {
      res.status(404).json({ error: 'Game not found' });
      return;
    }

    const query = `
      INSERT INTO moves (id, game_id, move_number, x, y, action, technique, confidence, reasoning, result)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(
      query,
      [id, row.id, move_number, x, y, action, technique, confidence, reasoning, result || 'pending'],
      function(err) {
        if (err) {
          res.status(500).json({ error: err.message });
        } else {
          res.json({ id, message: '✓ Move recorded' });
        }
      }
    );
  });
});

// Get moves for a game
app.get('/api/games/:game_id/moves', (req, res) => {
  const { game_id } = req.params;

  db.get('SELECT id FROM games WHERE game_id = ?', [game_id], (err, row) => {
    if (err || !row) {
      res.status(404).json({ error: 'Game not found' });
      return;
    }

    db.all(
      'SELECT * FROM moves WHERE game_id = ? ORDER BY move_number ASC',
      [row.id],
      (err, rows) => {
        if (err) {
          res.status(500).json({ error: err.message });
        } else {
          res.json(rows);
        }
      }
    );
  });
});

// ============== DEDUCTIONS ENDPOINTS ==============

// Record deductions
app.post('/api/games/:game_id/deductions', (req, res) => {
  const { game_id } = req.params;
  const { move_number, x, y, cell_type, technique, confidence, reasoning } = req.body;
  const id = uuidv4();

  db.get('SELECT id FROM games WHERE game_id = ?', [game_id], (err, row) => {
    if (err || !row) {
      res.status(404).json({ error: 'Game not found' });
      return;
    }

    const query = `
      INSERT INTO deductions (id, game_id, move_number, x, y, cell_type, technique, confidence, reasoning)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(
      query,
      [id, row.id, move_number, x, y, cell_type, technique, confidence, reasoning],
      function(err) {
        if (err) {
          res.status(500).json({ error: err.message });
        } else {
          res.json({ id, message: '✓ Deduction recorded' });
        }
      }
    );
  });
});

// Get deductions for a move
app.get('/api/games/:game_id/deductions/:move_number', (req, res) => {
  const { game_id, move_number } = req.params;

  db.get('SELECT id FROM games WHERE game_id = ?', [game_id], (err, row) => {
    if (err || !row) {
      res.status(404).json({ error: 'Game not found' });
      return;
    }

    db.all(
      'SELECT * FROM deductions WHERE game_id = ? AND move_number = ? ORDER BY timestamp ASC',
      [row.id, move_number],
      (err, rows) => {
        if (err) {
          res.status(500).json({ error: err.message });
        } else {
          res.json(rows);
        }
      }
    );
  });
});

// ============== STATISTICS ENDPOINTS ==============

// Get overall statistics
app.get('/api/statistics', (req, res) => {
  db.get(
    `SELECT 
      COUNT(*) as total_games,
      SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as total_wins,
      SUM(CASE WHEN lost = 1 THEN 1 ELSE 0 END) as total_losses,
      ROUND(SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as win_rate,
      ROUND(AVG(moves), 0) as average_moves
    FROM games
    WHERE result IS NOT NULL`,
    (err, row) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json(row || {});
      }
    }
  );
});

// Get statistics by difficulty
app.get('/api/statistics/by-difficulty', (req, res) => {
  db.all(
    `SELECT 
      difficulty,
      COUNT(*) as total_games,
      SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as total_wins,
      SUM(CASE WHEN lost = 1 THEN 1 ELSE 0 END) as total_losses,
      ROUND(SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as win_rate,
      ROUND(AVG(moves), 0) as average_moves
    FROM games
    WHERE result IS NOT NULL
    GROUP BY difficulty
    ORDER BY total_games DESC`,
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json(rows);
      }
    }
  );
});

// Get statistics by technique
app.get('/api/statistics/by-technique', (req, res) => {
  db.all(
    `SELECT 
      technique,
      COUNT(*) as usage_count,
      ROUND(AVG(confidence), 3) as average_confidence
    FROM deductions
    GROUP BY technique
    ORDER BY usage_count DESC`,
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json(rows);
      }
    }
  );
});

// Get statistics by platform
app.get('/api/statistics/by-platform', (req, res) => {
  db.all(
    `SELECT 
      platform,
      COUNT(*) as total_games,
      SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as total_wins,
      ROUND(SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as win_rate
    FROM games
    WHERE result IS NOT NULL
    GROUP BY platform`,
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json(rows);
      }
    }
  );
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString(), version: '1.0.0' });
});

// Start server
app.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 MINESWEEPER BOT BACKEND');
  console.log('='.repeat(60));
  console.log(`✓ Server running on http://localhost:${PORT}`);
  console.log(`✓ Database: ${dbPath}`);
  console.log(`✓ API Documentation: http://localhost:${PORT}/api/docs`);
  console.log('='.repeat(60) + '\n');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n✓ Shutting down gracefully...');
  db.close();
  process.exit(0);
});

module.exports = app;
