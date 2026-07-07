"""
Automated Minesweeper Player
Main execution loop to run the bot automatically
"""

import time
import sys
from typing import Optional
from minesweeper_bot import MinesweeperBot
from game_integration import (
    BotGameController,
    GamePlatform,
    MinesweeperOnlineAdapter
)


class AutomatedMinesweeperPlayer:
    """Orchestrates bot and game interaction"""
    
    def __init__(self, platform: GamePlatform = GamePlatform.MINESWEEPERONLINE):
        self.platform = platform
        self.adapter = None
        self.controller = None
        self.bot = None
        self.game_won = False
        self.game_lost = False
        self.start_time = None
    
    def start_game(self, url: str = None, difficulty: str = 'beginner') -> bool:
        """Start a new game"""
        print(f"\n🎮 Starting {difficulty} Minesweeper game...")
        print(f"Platform: {self.platform.value}")
        
        # Create adapter
        if self.platform == GamePlatform.MINESWEEPERONLINE:
            self.adapter = MinesweeperOnlineAdapter(headless=False)
        else:
            print(f"Unsupported platform: {self.platform}")
            return False
        
        # Connect
        self.controller = BotGameController(self.adapter)
        if not self.controller.connect(url):
            print("❌ Failed to connect to game")
            return False
        
        # Sync initial state
        if not self.controller.sync_board_state():
            print("❌ Failed to read game state")
            return False
        
        # Initialize bot
        state = self.controller.game_state
        self.bot = MinesweeperBot(
            width=state.board_width,
            height=state.board_height,
            mines=state.mines
        )
        
        print(f"✓ Connected!")
        print(f"  Board: {state.board_width}×{state.board_height}")
        print(f"  Mines: {state.mines}")
        print(f"  Difficulty: {difficulty}")
        
        self.start_time = time.time()
        return True
    
    def play_game(self, max_moves: int = 1000, verbose: bool = True) -> bool:
        """Play the game with the bot"""
        if not self.bot or not self.controller:
            print("❌ Game not started")
            return False
        
        print("\n🤖 Bot is playing...\n")
        move_count = 0
        
        try:
            while move_count < max_moves:
                # Sync board state
                if not self.controller.sync_board_state():
                    print("\n❌ Lost connection to game")
                    break
                
                state = self.controller.game_state
                
                # Check game status
                if state.game_status == 'won':
                    print("\n🎉 GAME WON!")
                    self.game_won = True
                    break
                elif state.game_status == 'lost':
                    print("\n💣 GAME LOST!")
                    self.game_lost = True
                    break
                
                # Update bot's board knowledge
                self.bot.update_board_state(state.cells)
                
                # Get recommended move
                move = self.bot.get_recommended_move()
                if not move:
                    print("\n⚠️  No valid moves found")
                    break
                
                x, y, action, technique, confidence = move
                
                # Display move info
                if verbose:
                    elapsed = time.time() - self.start_time
                    print(f"Move {move_count + 1} [{elapsed:.1f}s]: {action.upper()} [{x}, {y}]")
                    print(f"  Technique: {technique}")
                    print(f"  Confidence: {confidence*100:.1f}%")
                
                # Execute move
                if not self.controller.play_move(x, y, action):
                    print(f"\n❌ Failed to execute move at [{x}, {y}]")
                    break
                
                # Record move
                self.bot.record_move(x, y, action, technique, confidence)
                
                move_count += 1
        
        except KeyboardInterrupt:
            print("\n⏸️  Game paused by user")
        
        # Print final statistics
        elapsed = time.time() - self.start_time
        print(f"\n⏱️  Game duration: {elapsed:.1f}s")
        self.controller.print_stats()
        self.bot.print_status()
        
        return self.game_won
    
    def stop_game(self):
        """Stop the game and cleanup"""
        if self.controller:
            self.controller.disconnect()
        print("\n✓ Game stopped")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("AUTOMATED MINESWEEPER BOT")
    print("="*60)
    
    # Create player
    player = AutomatedMinesweeperPlayer(
        platform=GamePlatform.MINESWEEPERONLINE
    )
    
    try:
        # Start game
        if not player.start_game(difficulty='beginner'):
            return False
        
        # Play game
        player.play_game(verbose=True)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        player.stop_game()
    
    print("\n" + "="*60)
    return player.game_won


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
