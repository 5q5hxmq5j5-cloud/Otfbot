"""
Minesweeper Bot Core Controller
Decides when to play, flag, or wait based on constraint analysis
"""

import time
from typing import List, Tuple, Optional, Dict
from constraint_solver import ConstraintSatisfactionSolver, CellType


class MinesweeperBot:
    """
    Core bot controller that coordinates constraint solving with gameplay decisions
    """
    
    def __init__(self, width: int, height: int, mines: int):
        """Initialize the bot"""
        self.width = width
        self.height = height
        self.total_mines = mines
        self.solver = ConstraintSatisfactionSolver(width, height, mines)
        self.move_count = 0
        self.flagged_count = 0
        self.revealed_count = 0
        self.move_history = []
    
    def update_board_state(self, cells: Dict[Tuple[int, int], Dict]):
        """Update bot's understanding of board from game state"""
        for (x, y), cell_info in cells.items():
            if cell_info['state'] == 'revealed':
                self.solver.set_cell(x, y, 'revealed', cell_info.get('value', 0))
                self.revealed_count = max(self.revealed_count, len([c for c in cells.values() if c['state'] == 'revealed']))
            elif cell_info['state'] == 'flagged':
                self.solver.set_cell(x, y, 'flagged')
                self.flagged_count = max(self.flagged_count, len([c for c in cells.values() if c['state'] == 'flagged']))
    
    def analyze_board(self) -> List:
        """Run constraint satisfaction solver and get deductions"""
        return self.solver.solve()
    
    def get_recommended_move(self) -> Optional[Tuple[int, int, str, str, float]]:
        """
        Get the recommended move based on analysis
        Returns: (x, y, action, technique, confidence) or None
        """
        deductions = self.analyze_board()
        
        if not deductions:
            return None
        
        # Prioritize certain moves
        certain_mines = [d for d in deductions if d.cell_type == CellType.MINE and d.confidence == 1.0]
        certain_safe = [d for d in deductions if d.cell_type == CellType.SAFE and d.confidence == 1.0]
        
        # Flag certain mines first
        if certain_mines:
            d = certain_mines[0]
            return (d.cell[0], d.cell[1], 'flag', d.technique, d.confidence)
        
        # Click certain safe cells
        if certain_safe:
            d = certain_safe[0]
            return (d.cell[0], d.cell[1], 'click', d.technique, d.confidence)
        
        # Return highest confidence move
        best = max(deductions, key=lambda d: d.confidence)
        action = 'flag' if best.cell_type == CellType.MINE else 'click'
        return (best.cell[0], best.cell[1], action, best.technique, best.confidence)
    
    def suggest_moves(self, count: int = 5) -> List[Tuple[int, int, str, str, float]]:
        """Get top N recommended moves"""
        deductions = self.analyze_board()
        
        if not deductions:
            return []
        
        # Sort by confidence, then by type (mines first)
        sorted_deductions = sorted(
            deductions,
            key=lambda d: (d.cell_type == CellType.MINE, d.confidence),
            reverse=True
        )
        
        moves = []
        for d in sorted_deductions[:count]:
            action = 'flag' if d.cell_type == CellType.MINE else 'click'
            moves.append((d.cell[0], d.cell[1], action, d.technique, d.confidence))
        
        return moves
    
    def record_move(self, x: int, y: int, action: str, technique: str, confidence: float, result: str = 'pending'):
        """Record a move in history"""
        self.move_count += 1
        self.move_history.append({
            'number': self.move_count,
            'x': x,
            'y': y,
            'action': action,
            'technique': technique,
            'confidence': confidence,
            'result': result,
            'timestamp': time.time()
        })
    
    def get_statistics(self) -> Dict:
        """Get bot statistics"""
        safe_deductions = self.solver.get_safe_cells()
        mine_deductions = self.solver.get_mine_cells()
        
        return {
            'total_moves': self.move_count,
            'safe_cells_deduced': len(safe_deductions),
            'mines_deduced': len(mine_deductions),
            'flagged': self.flagged_count,
            'revealed': self.revealed_count,
            'move_history': self.move_history
        }
    
    def print_status(self):
        """Print current bot status"""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("BOT STATUS")
        print("="*60)
        print(f"Moves Made: {stats['total_moves']}")
        print(f"Safe Cells Deduced: {stats['safe_cells_deduced']}")
        print(f"Mines Deduced: {stats['mines_deduced']}")
        print(f"Flagged: {stats['flagged']}")
        print(f"Revealed: {stats['revealed']}")
        print("="*60)
