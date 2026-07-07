/**
 * Database initialization and utilities
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbDir = path.join(__dirname, 'data');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const dbPath = path.join(dbDir, 'minesweeper.db');

class Database {
  constructor() {
    this.db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Database connection error:', err);
      } else {
        console.log('✓ Connected to database');
        this.initialize();
      }
    });
  }

  initialize() {
    this.db.serialize(() => {
      // Games table
      this.db.run(`
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
      this.db.run(`
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
      this.db.run(`
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
      this.db.run(`
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

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve(this);
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  close() {
    return new Promise((resolve, reject) => {
      this.db.close((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
}

module.exports = new Database();
