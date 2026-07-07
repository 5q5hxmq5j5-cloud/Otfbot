"""
Real-time Analysis Dashboard
Console-based UI for monitoring bot analysis and gameplay

Usage:
    python -c "from dashboard import run_dashboard; run_dashboard()"
"""

import curses
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class UIColor(Enum):
    """Terminal color definitions"""
    DEFAULT = 1
    HEADER = 2
    SUCCESS = 3
    ERROR = 4
    WARNING = 5
    INFO = 6
    SAFE_CELL = 7
    MINE_CELL = 8
    UNKNOWN_CELL = 9


@dataclass
class DashboardState:
    """Current dashboard state"""
    game_id: str
    board_width: int
    board_height: int
    total_mines: int
    current_move: int
    safe_cells_found: int
    mine_cells_found: int
    game_status: str  # 'playing', 'won', 'lost'
    elapsed_time: float
    board_state: Dict  # Current board visualization
    recent_deductions: List[str]
    recent_moves: List[str]
    stats: Dict  # Overall statistics


class MinesweeperDashboard:
    """Real-time console dashboard for Minesweeper bot"""
    
    def __init__(self, stdscr):
        """Initialize dashboard with curses window"""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.state = None
        self.start_time = time.time()
        
        self._init_colors()
    
    def _init_colors(self):
        """Initialize color pairs"""
        curses.init_pair(UIColor.HEADER.value, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(UIColor.SUCCESS.value, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(UIColor.ERROR.value, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(UIColor.WARNING.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(UIColor.INFO.value, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(UIColor.SAFE_CELL.value, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(UIColor.MINE_CELL.value, curses.COLOR_RED, curses.COLOR_BLACK)
    
    def update(self, state: DashboardState):
        """Update dashboard with new state"""
        self.state = state
        self._draw()
    
    def _draw(self):
        """Draw complete dashboard"""
        self.stdscr.clear()
        
        try:
            self._draw_header()
            self._draw_stats_panel()
            self._draw_board_panel()
            self._draw_deductions_panel()
            self._draw_moves_panel()
            self._draw_footer()
            
            self.stdscr.refresh()
        except curses.error:
            pass
    
    def _draw_header(self):
        """Draw header"""
        header = " 🤖 MINESWEEPER BOT DASHBOARD "
        try:
            self.stdscr.addstr(0, 0, "=" * self.width, curses.color_pair(UIColor.HEADER.value))
            self.stdscr.addstr(
                1, 
                max(0, (self.width - len(header)) // 2), 
                header,
                curses.color_pair(UIColor.HEADER.value) | curses.A_BOLD
            )
            self.stdscr.addstr(2, 0, "=" * self.width, curses.color_pair(UIColor.HEADER.value))
        except curses.error:
            pass
    
    def _draw_stats_panel(self):
        """Draw statistics panel"""
        row = 4
        
        if self.state:
            elapsed = time.time() - self.start_time
            time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
            
            try:
                self.stdscr.addstr(row, 2, "📊 GAME STATUS", curses.color_pair(UIColor.INFO.value) | curses.A_BOLD)
            except curses.error:
                pass
            row += 1
            
            info_items = [
                f"Game ID: {self.state.game_id[:8]}...",
                f"Board: {self.state.board_width}×{self.state.board_height} | Mines: {self.state.total_mines}",
                f"Move: {self.state.current_move} | Time: {time_str}",
                f"Status: {self.state.game_status.upper()}",
            ]
            
            for item in info_items:
                try:
                    self.stdscr.addstr(row, 4, item, curses.color_pair(UIColor.DEFAULT.value))
                    row += 1
                except curses.error:
                    pass
            
            row += 1
            
            try:
                self.stdscr.addstr(row, 2, "🎯 DEDUCTIONS", curses.color_pair(UIColor.INFO.value) | curses.A_BOLD)
            except curses.error:
                pass
            row += 1
            
            safe_str = f"✅ Safe Cells: {self.state.safe_cells_found}"
            mine_str = f"🚩 Mine Cells: {self.state.mine_cells_found}"
            
            try:
                self.stdscr.addstr(row, 4, safe_str, curses.color_pair(UIColor.SAFE_CELL.value))
                self.stdscr.addstr(row, 30, mine_str, curses.color_pair(UIColor.MINE_CELL.value))
                row += 2
            except curses.error:
                pass
    
    def _draw_board_panel(self):
        """Draw board visualization"""
        row = 15
        
        try:
            self.stdscr.addstr(row, 2, "📋 BOARD STATE", curses.color_pair(UIColor.INFO.value) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        
        if self.state and self.state.board_state:
            board = self.state.board_state
            
            for y in range(min(self.state.board_height, 8)):
                line = "   "
                for x in range(min(self.state.board_width, 16)):
                    if (x, y) in board:
                        cell = board[(x, y)]
                        if cell == 'F':
                            line += "🚩"
                        elif cell == '?':
                            line += "□"
                        elif cell == '0':
                            line += " "
                        else:
                            line += str(cell)
                    else:
                        line += "?"
                    line += " "
                
                try:
                    self.stdscr.addstr(row, 2, line)
                    row += 1
                except curses.error:
                    pass
    
    def _draw_deductions_panel(self):
        """Draw recent deductions"""
        row = 26
        
        try:
            self.stdscr.addstr(row, 2, "💡 RECENT DEDUCTIONS", curses.color_pair(UIColor.INFO.value) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        
        if self.state and self.state.recent_deductions:
            for deduction in self.state.recent_deductions[:3]:
                try:
                    self.stdscr.addstr(row, 4, f"• {deduction}", curses.color_pair(UIColor.DEFAULT.value))
                    row += 1
                except curses.error:
                    pass
    
    def _draw_moves_panel(self):
        """Draw recent moves"""
        row = 30
        
        try:
            self.stdscr.addstr(row, 40, "🎮 RECENT MOVES", curses.color_pair(UIColor.INFO.value) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        
        if self.state and self.state.recent_moves:
            for move in self.state.recent_moves[:3]:
                try:
                    self.stdscr.addstr(row, 42, f"• {move}", curses.color_pair(UIColor.DEFAULT.value))
                    row += 1
                except curses.error:
                    pass
    
    def _draw_footer(self):
        """Draw footer"""
        footer = "Press 'q' to quit | 'p' to pause | Space for next"
        try:
            self.stdscr.addstr(
                self.height - 1, 
                2, 
                footer, 
                curses.color_pair(UIColor.INFO.value) | curses.A_DIM
            )
        except curses.error:
            pass


def run_dashboard(callback=None):
    """Run dashboard in curses mode"""
    def main(stdscr):
        stdscr.nodelay(True)
        curses.curs_set(0)
        
        dashboard = MinesweeperDashboard(stdscr)
        
        example_state = DashboardState(
            game_id="abc123def456",
            board_width=16,
            board_height=16,
            total_mines=40,
            current_move=15,
            safe_cells_found=42,
            mine_cells_found=8,
            game_status="playing",
            elapsed_time=120.5,
            board_state={
                (0, 0): '1', (1, 0): '□', (2, 0): '?',
                (0, 1): '0', (1, 1): '2', (2, 1): '🚩',
            },
            recent_deductions=[
                "Basic Constraint: [3,4] is safe",
                "Hidden Single: [5,6] must be mine",
                "Naked Single: [7,8] is safe",
            ],
            recent_moves=[
                "Move 15: Click [3,4] - Basic",
                "Move 14: Flag [5,6] - Hidden",
                "Move 13: Click [1,2] - Prob",
            ],
            stats={
                'total_games': 150,
                'total_wins': 127,
                'win_rate': 84.7,
            }
        )
        
        running = True
        while running:
            dashboard.update(example_state)
            
            try:
                ch = stdscr.getch()
                if ch == ord('q'):
                    running = False
            except:
                pass
            
            time.sleep(0.1)
    
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_dashboard()
