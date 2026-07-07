"""
Game Integration Module
Vision/API connection to read the actual board state
"""

import time
from typing import Dict, Tuple, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class GamePlatform(Enum):
    """Supported online Minesweeper platforms"""
    MINESWEEPERONLINE = "minesweeperonline"
    MICROSOFT = "microsoft"
    CUSTOM = "custom"


@dataclass
class GameState:
    """Current game state snapshot"""
    board_width: int
    board_height: int
    mines: int
    cells: Dict[Tuple[int, int], Dict]  # {(x, y): {'state': str, 'value': int}}
    game_status: str  # 'playing', 'won', 'lost'
    time_elapsed: int
    flags_placed: int


class GameAdapter(ABC):
    """Abstract base class for game platform adapters"""
    
    @abstractmethod
    def connect(self, url: str) -> bool:
        pass
    
    @abstractmethod
    def get_game_state(self) -> Optional[GameState]:
        pass
    
    @abstractmethod
    def click_cell(self, x: int, y: int) -> bool:
        pass
    
    @abstractmethod
    def flag_cell(self, x: int, y: int) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass


class MinesweeperOnlineAdapter(GameAdapter):
    """Integration with minesweeperonline.com"""
    
    def __init__(self, headless: bool = True):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not installed. Run: pip install selenium")
        
        self.driver = None
        self.headless = headless
        self.url = "https://minesweeperonline.com"
    
    def connect(self, url: str = None) -> bool:
        """Connect to game"""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(url or self.url)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "square"))
            )
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_game_state(self) -> Optional[GameState]:
        """Extract current board state"""
        try:
            board = self.driver.find_element(By.CLASS_NAME, "board")
            cells = board.find_elements(By.CLASS_NAME, "square")
            
            board_size = int(len(cells) ** 0.5)
            board_width = board_height = board_size
            
            cell_dict = {}
            for i, cell in enumerate(cells):
                x = i % board_width
                y = i // board_width
                
                classes = cell.get_attribute("class")
                state = self._parse_cell_state(classes)
                value = self._parse_cell_value(cell)
                
                cell_dict[(x, y)] = {'state': state, 'value': value, 'element': cell}
            
            game_status = self._get_game_status()
            flags_placed = self._get_flag_count()
            mines = board_width * board_height // 5
            
            return GameState(
                board_width=board_width,
                board_height=board_height,
                mines=mines,
                cells=cell_dict,
                game_status=game_status,
                time_elapsed=0,
                flags_placed=flags_placed
            )
        except Exception as e:
            print(f"Error reading game state: {e}")
            return None
    
    def click_cell(self, x: int, y: int) -> bool:
        """Left-click a cell"""
        try:
            state = self.get_game_state()
            if state and (x, y) in state.cells:
                state.cells[(x, y)]['element'].click()
                time.sleep(0.2)
                return True
        except Exception as e:
            print(f"Click failed: {e}")
        return False
    
    def flag_cell(self, x: int, y: int) -> bool:
        """Right-click to flag a cell"""
        try:
            state = self.get_game_state()
            if state and (x, y) in state.cells:
                ActionChains(self.driver).right_click(state.cells[(x, y)]['element']).perform()
                time.sleep(0.2)
                return True
        except Exception as e:
            print(f"Flag failed: {e}")
        return False
    
    def disconnect(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
    
    def _parse_cell_state(self, classes: str) -> str:
        """Parse cell state from CSS classes"""
        if 'opened' in classes:
            return 'revealed'
        elif 'flagged' in classes:
            return 'flagged'
        else:
            return 'unknown'
    
    def _parse_cell_value(self, cell_element) -> int:
        """Parse number displayed on cell"""
        text = cell_element.text.strip()
        if text.isdigit():
            return int(text)
        return 0
    
    def _get_game_status(self) -> str:
        """Get game status"""
        try:
            face = self.driver.find_element(By.CLASS_NAME, "smiley")
            classes = face.get_attribute("class")
            if 'smiley-dead' in classes:
                return 'lost'
            elif 'smiley-win' in classes:
                return 'won'
        except:
            pass
        return 'playing'
    
    def _get_flag_count(self) -> int:
        """Get number of flags placed"""
        try:
            counter = self.driver.find_element(By.CLASS_NAME, "counter")
            return int(counter.text) if counter.text.isdigit() else 0
        except:
            return 0


class BotGameController:
    """Controller managing bot and game interaction"""
    
    def __init__(self, adapter: GameAdapter):
        self.adapter = adapter
        self.game_state = None
        self.move_history = []
        self.stats = {
            'moves_made': 0,
            'cells_clicked': 0,
            'cells_flagged': 0,
            'game_won': False,
            'game_lost': False
        }
    
    def connect(self, url: str = None) -> bool:
        """Connect to game"""
        return self.adapter.connect(url)
    
    def sync_board_state(self) -> bool:
        """Sync board state from game"""
        self.game_state = self.adapter.get_game_state()
        return self.game_state is not None
    
    def play_move(self, x: int, y: int, action: str = 'click') -> bool:
        """Execute a move"""
        if action == 'click':
            success = self.adapter.click_cell(x, y)
            if success:
                self.stats['cells_clicked'] += 1
        elif action == 'flag':
            success = self.adapter.flag_cell(x, y)
            if success:
                self.stats['cells_flagged'] += 1
        else:
            return False
        
        if success:
            self.stats['moves_made'] += 1
            self.move_history.append((x, y, action))
            time.sleep(0.5)
            return True
        return False
    
    def check_game_status(self) -> str:
        """Check if game is won/lost"""
        state = self.adapter.get_game_state()
        if state:
            if state.game_status == 'won':
                self.stats['game_won'] = True
            elif state.game_status == 'lost':
                self.stats['game_lost'] = True
            return state.game_status
        return 'unknown'
    
    def print_stats(self):
        """Print statistics"""
        print("\n" + "="*60)
        print("GAME STATISTICS")
        print("="*60)
        print(f"Total Moves: {self.stats['moves_made']}")
        print(f"Cells Clicked: {self.stats['cells_clicked']}")
        print(f"Cells Flagged: {self.stats['cells_flagged']}")
        print(f"Game Won: {'✓' if self.stats['game_won'] else '✗'}")
        print(f"Game Lost: {'✓' if self.stats['game_lost'] else '✗'}")
        print("="*60)
    
    def disconnect(self):
        """Disconnect from game"""
        self.adapter.disconnect()
