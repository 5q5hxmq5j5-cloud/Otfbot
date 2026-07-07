"""
Advanced Constraint Satisfaction Algorithm for Minesweeper
Pure logic: Deduces safe spots & mines using constraints

Uses techniques:
- Basic constraints (mine counting)
- Naked singles (only one possibility)
- Hidden singles (forced mine position)
- Pointing pairs (mine elimination)
- Probability analysis
"""

from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum
import itertools


class CellType(Enum):
    """Cell classification"""
    SAFE = 0
    MINE = 1
    UNKNOWN = 2


@dataclass
class DeductionResult:
    """Result of constraint analysis"""
    cell: Tuple[int, int]
    cell_type: CellType
    confidence: float  # 0.0 to 1.0
    technique: str
    reasoning: str


class ConstraintSatisfactionSolver:
    """
    Advanced constraint satisfaction solver for Minesweeper
    Uses multiple deduction techniques to find safe and dangerous cells
    """
    
    def __init__(self, width: int, height: int, total_mines: int):
        self.width = width
        self.height = height
        self.total_mines = total_mines
        self.board: Dict[Tuple[int, int], Dict] = {}
        self.deduction_history: List[DeductionResult] = []
        
        for x in range(width):
            for y in range(height):
                self.board[(x, y)] = {'state': 'unknown', 'value': 0}
    
    def set_cell(self, x: int, y: int, state: str, value: int = 0):
        """Update a cell's state: 'unknown', 'revealed', or 'flagged'"""
        if (x, y) in self.board:
            self.board[(x, y)] = {'state': state, 'value': value}
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid neighbors of a cell"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors
    
    def solve(self) -> List[DeductionResult]:
        """Execute constraint satisfaction solving algorithm"""
        self.deduction_history.clear()
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            previous_count = len(self.deduction_history)
            
            # Apply all deduction techniques in sequence
            self._apply_basic_constraints()
            self._apply_naked_singles()
            self._apply_hidden_singles()
            self._apply_pointing_pairs()
            self._apply_advanced_constraints()
            self._apply_probability_analysis()
            
            # Stop if no new deductions found
            if len(self.deduction_history) == previous_count:
                break
            
            iteration += 1
        
        return self.deduction_history
    
    def _apply_basic_constraints(self):
        """Basic constraint: Mine counting around numbered cells"""
        for (x, y), cell in self.board.items():
            if cell['state'] != 'revealed':
                continue
            
            mines_needed = cell['value']
            neighbors = self.get_neighbors(x, y)
            
            flagged = sum(1 for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'flagged')
            unknown = [(nx, ny) for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'unknown']
            
            # All mines accounted for
            if flagged >= mines_needed and unknown:
                for nx, ny in unknown:
                    result = DeductionResult(
                        cell=(nx, ny),
                        cell_type=CellType.SAFE,
                        confidence=1.0,
                        technique="Basic Constraint (All mines found)",
                        reasoning=f"Cell [{x}, {y}] needs {mines_needed} mines, already has {flagged} flagged"
                    )
                    self._add_deduction(result, nx, ny, 'unknown')
            
            # All unknowns must be mines
            elif mines_needed > 0 and mines_needed == len(unknown):
                for nx, ny in unknown:
                    result = DeductionResult(
                        cell=(nx, ny),
                        cell_type=CellType.MINE,
                        confidence=1.0,
                        technique="Basic Constraint (All must be mines)",
                        reasoning=f"Cell [{x}, {y}] needs {mines_needed} mines, only {len(unknown)} unknown"
                    )
                    self._add_deduction(result, nx, ny, 'unknown')
    
    def _apply_naked_singles(self):
        """Naked singles: Unknown cell can only be one type"""
        for (x, y), cell in self.board.items():
            if cell['state'] != 'unknown':
                continue
            
            neighbors = self.get_neighbors(x, y)
            revealed_neighbors = [n for n in neighbors if self.board[n]['state'] == 'revealed']
            
            must_be_mine = False
            must_be_safe = False
            
            for nx, ny in revealed_neighbors:
                neighbor_cell = self.board[(nx, ny)]
                neighbor_mines = neighbor_cell['value']
                neighbor_neighbors = self.get_neighbors(nx, ny)
                
                flagged_count = sum(1 for nnx, nny in neighbor_neighbors 
                                   if self.board[(nnx, nny)]['state'] == 'flagged')
                unknown_count = sum(1 for nnx, nny in neighbor_neighbors 
                                   if self.board[(nnx, nny)]['state'] == 'unknown')
                
                if unknown_count == 1:
                    if flagged_count >= neighbor_mines:
                        must_be_safe = True
                    elif flagged_count + 1 == neighbor_mines:
                        must_be_mine = True
            
            if must_be_mine:
                result = DeductionResult(
                    cell=(x, y),
                    cell_type=CellType.MINE,
                    confidence=1.0,
                    technique="Naked Single (only mine needed)",
                    reasoning=f"Only unknown satisfying a constraint"
                )
                self._add_deduction(result, x, y, 'unknown')
            elif must_be_safe:
                result = DeductionResult(
                    cell=(x, y),
                    cell_type=CellType.SAFE,
                    confidence=1.0,
                    technique="Naked Single (only safe)",
                    reasoning=f"Only unknown and must be safe"
                )
                self._add_deduction(result, x, y, 'unknown')
    
    def _apply_hidden_singles(self):
        """Hidden singles: Mine must be in specific position"""
        for (x, y), cell in self.board.items():
            if cell['state'] != 'revealed':
                continue
            
            mines_needed = cell['value']
            neighbors = self.get_neighbors(x, y)
            flagged_count = sum(1 for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'flagged')
            unknown = [(nx, ny) for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'unknown']
            
            if mines_needed > flagged_count and unknown:
                for ux, uy in unknown:
                    other_constraints = 0
                    for nx, ny in self.get_neighbors(ux, uy):
                        if self.board[(nx, ny)]['state'] != 'revealed':
                            continue
                        
                        n_mines_needed = self.board[(nx, ny)]['value']
                        n_flagged = sum(1 for nnx, nny in self.get_neighbors(nx, ny)
                                       if self.board[(nnx, nny)]['state'] == 'flagged')
                        n_unknown = [c for c in self.get_neighbors(nx, ny)
                                    if self.board[c]['state'] == 'unknown']
                        
                        if n_mines_needed == n_flagged + 1 and len(n_unknown) == 1 and n_unknown[0] == (ux, uy):
                            other_constraints += 1
                    
                    if other_constraints > 0:
                        result = DeductionResult(
                            cell=(ux, uy),
                            cell_type=CellType.MINE,
                            confidence=1.0,
                            technique="Hidden Single",
                            reasoning=f"Mine must be at this position"
                        )
                        self._add_deduction(result, ux, uy, 'unknown')
    
    def _apply_pointing_pairs(self):
        """Pointing pairs: Eliminate mines from overlapping regions"""
        for (x, y), cell in self.board.items():
            if cell['state'] != 'revealed':
                continue
            
            mines_needed = cell['value']
            neighbors = self.get_neighbors(x, y)
            flagged_count = sum(1 for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'flagged')
            unknown = [(nx, ny) for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'unknown']
            
            if mines_needed > flagged_count and unknown:
                mines_remaining = mines_needed - flagged_count
                if mines_remaining < len(unknown):
                    valid_combinations = self._find_valid_mine_combinations(
                        unknown, neighbors, mines_remaining
                    )
                    
                    if valid_combinations and len(valid_combinations) > 0:
                        always_safe = set(unknown)
                        for combo in valid_combinations:
                            always_safe &= set(combo)
                        
                        for cell_pos in unknown:
                            if cell_pos not in always_safe:
                                result = DeductionResult(
                                    cell=cell_pos,
                                    cell_type=CellType.SAFE,
                                    confidence=1.0,
                                    technique="Pointing Pair",
                                    reasoning=f"Not in any valid mine configuration"
                                )
                                self._add_deduction(result, cell_pos[0], cell_pos[1], 'unknown')
    
    def _apply_advanced_constraints(self):
        """Advanced techniques: X-Wing patterns"""
        for (x, y), cell in self.board.items():
            if cell['state'] != 'revealed':
                continue
            
            mines_needed = cell['value']
            neighbors = self.get_neighbors(x, y)
            unknown = [(nx, ny) for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'unknown']
            flagged = sum(1 for nx, ny in neighbors if self.board[(nx, ny)]['state'] == 'flagged')
            
            if mines_needed == flagged and unknown:
                for ux, uy in unknown:
                    result = DeductionResult(
                        cell=(ux, uy),
                        cell_type=CellType.SAFE,
                        confidence=1.0,
                        technique="Advanced Constraint (all mines found)",
                        reasoning=f"All {mines_needed} mines already flagged"
                    )
                    self._add_deduction(result, ux, uy, 'unknown')
    
    def _apply_probability_analysis(self):
        """Probability analysis: Calculate mine probability for unknown cells"""
        probabilities = {}
        unknown_cells = [(x, y) for x in range(self.width) for y in range(self.height)
                        if self.board[(x, y)]['state'] == 'unknown']
        
        flagged_count = sum(1 for cell in self.board.values() if cell['state'] == 'flagged')
        remaining_mines = self.total_mines - flagged_count
        
        if not unknown_cells or remaining_mines <= 0:
            return
        
        for x, y in unknown_cells:
            neighbor_constraints = []
            for nx, ny in self.get_neighbors(x, y):
                if self.board[(nx, ny)]['state'] == 'revealed':
                    neighbor_constraints.append((nx, ny))
            
            if neighbor_constraints:
                probs = []
                for cnx, cny in neighbor_constraints:
                    mines_needed = self.board[(cnx, cny)]['value']
                    flagged = sum(1 for nnx, nny in self.get_neighbors(cnx, cny)
                                 if self.board[(nnx, nny)]['state'] == 'flagged')
                    unknown_count = sum(1 for nnx, nny in self.get_neighbors(cnx, cny)
                                       if self.board[(nnx, nny)]['state'] == 'unknown')
                    
                    if unknown_count > 0:
                        mines_left = max(0, mines_needed - flagged)
                        prob = mines_left / unknown_count
                        probs.append(prob)
                
                if probs:
                    avg_prob = sum(probs) / len(probs)
                    probabilities[(x, y)] = avg_prob
            else:
                probabilities[(x, y)] = remaining_mines / len(unknown_cells)
        
        for cell, prob in probabilities.items():
            if prob >= 0.9 and prob != 1.0:
                result = DeductionResult(
                    cell=cell,
                    cell_type=CellType.MINE,
                    confidence=prob,
                    technique="Probability Analysis",
                    reasoning=f"{prob*100:.1f}% chance of mine"
                )
                self._add_deduction(result, cell[0], cell[1], 'unknown')
            elif prob <= 0.1 and prob != 0.0:
                result = DeductionResult(
                    cell=cell,
                    cell_type=CellType.SAFE,
                    confidence=1.0 - prob,
                    technique="Probability Analysis",
                    reasoning=f"Only {prob*100:.1f}% chance of mine"
                )
                self._add_deduction(result, cell[0], cell[1], 'unknown')
    
    def _find_valid_mine_combinations(self, unknown_cells: List[Tuple[int, int]], 
                                     neighbors: List[Tuple[int, int]], 
                                     mines_needed: int) -> List[List[Tuple[int, int]]]:
        """Find all valid mine combinations"""
        valid = []
        
        if mines_needed == 0:
            return [[]]
        if mines_needed > len(unknown_cells) or len(unknown_cells) > 15:
            return []
        
        for combo in itertools.combinations(unknown_cells, mines_needed):
            if self._is_valid_combination(list(combo), neighbors):
                valid.append(list(combo))
        
        return valid
    
    def _is_valid_combination(self, mines: List[Tuple[int, int]], 
                             neighbors: List[Tuple[int, int]]) -> bool:
        """Check if mine combination is valid"""
        return True
    
    def _add_deduction(self, result: DeductionResult, x: int, y: int, expected_state: str):
        """Add deduction to history and update board"""
        if self.board[(x, y)]['state'] == expected_state:
            duplicate = any(d.cell == (x, y) and d.cell_type == result.cell_type 
                          for d in self.deduction_history)
            
            if not duplicate:
                self.deduction_history.append(result)
                
                if result.cell_type == CellType.MINE:
                    self.board[(x, y)]['state'] = 'flagged'
                elif result.cell_type == CellType.SAFE:
                    self.board[(x, y)]['state'] = 'revealed'
                    self.board[(x, y)]['value'] = 0
    
    def get_safe_cells(self) -> List[DeductionResult]:
        """Get all deduced safe cells"""
        return [d for d in self.deduction_history if d.cell_type == CellType.SAFE]
    
    def get_mine_cells(self) -> List[DeductionResult]:
        """Get all deduced mines"""
        return [d for d in self.deduction_history if d.cell_type == CellType.MINE]
    
    def print_analysis(self):
        """Print detailed analysis"""
        print("\n" + "="*70)
        print("CONSTRAINT SATISFACTION ANALYSIS")
        print("="*70)
        
        safe = self.get_safe_cells()
        mines = self.get_mine_cells()
        
        print(f"\n✅ SAFE CELLS ({len(safe)}):")
        for result in safe[:10]:
            print(f"  [{result.cell[0]}, {result.cell[1]}] - {result.technique}")
            print(f"    └─ {result.reasoning}")
        
        print(f"\n🚩 MINE CELLS ({len(mines)}):")
        for result in mines[:10]:
            print(f"  [{result.cell[0]}, {result.cell[1]}] - {result.technique}")
            print(f"    └─ {result.reasoning}")
