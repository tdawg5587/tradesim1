import pygame
import numpy as np
import pandas as pd
import time
import threading
import keyboard
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

class CandlestickGenerator:
    """Generates realistic candlestick data for practice"""
    
    def __init__(self, initial_price: float = 100.0):
        self.current_price = initial_price
        self.trend = random.choice([1, -1])  # 1 for uptrend, -1 for downtrend
        self.trend_strength = random.uniform(0.1, 0.3)
        self.volatility = random.uniform(0.5, 2.0)
        self.candles = []
        
    def generate_candle(self) -> dict:
        """Generate a single candlestick"""
        # Add some trend and randomness
        base_move = self.trend * self.trend_strength * random.uniform(0.5, 1.5)
        random_move = random.uniform(-self.volatility, self.volatility)
        
        open_price = self.current_price
        close_price = open_price + base_move + random_move
        
        # Generate high and low
        high_price = max(open_price, close_price) + random.uniform(0, self.volatility * 0.5)
        low_price = min(open_price, close_price) - random.uniform(0, self.volatility * 0.5)
        
        # Occasionally change trend
        if random.random() < 0.05:  # 5% chance to change trend
            self.trend *= -1
            self.trend_strength = random.uniform(0.1, 0.3)
            self.volatility = random.uniform(0.5, 2.0)
        
        self.current_price = close_price
        
        candle = {
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'timestamp': datetime.now()
        }
        
        self.candles.append(candle)
        return candle

class TradeScalpTrainer:
    """Main application class for the scalping trainer"""
    
    def __init__(self):
        pygame.init()
        
        # Screen settings
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Scalp Trading Trainer")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        
        # Data and timing
        self.candlestick_gen = CandlestickGenerator()
        self.candles_display = []  # Last N candles to display
        self.max_candles_display = 50
        
        # Game state
        self.running = True
        self.paused = False
        self.current_candle_start_time = None
        self.breakout_detected = False
        self.breakout_time = None
        self.trade_entered = False
        self.trade_entry_time = None
        self.reaction_times = []
        
        # Performance tracking
        self.total_breakouts = 0
        self.successful_entries = 0
        self.average_reaction_time = 0
        
        # Chart settings
        self.chart_x = 50
        self.chart_y = 50
        self.chart_width = 800
        self.chart_height = 400
        
        # Generate initial candles
        for _ in range(self.max_candles_display):
            self.candles_display.append(self.candlestick_gen.generate_candle())
        
        # Start the candle generation thread
        self.candle_thread = threading.Thread(target=self.candle_generation_loop, daemon=True)
        self.candle_thread.start()
        
        # Setup keyboard listeners
        self.setup_hotkeys()
        
    def setup_hotkeys(self):
        """Setup global hotkeys for trading actions"""
        # Entry trades: Shift + A, S, D
        keyboard.add_hotkey('shift+a', lambda: self.enter_trade('long'))
        keyboard.add_hotkey('shift+s', lambda: self.enter_trade('short'))
        keyboard.add_hotkey('shift+d', lambda: self.enter_trade('breakout'))
        
        # Cancel trade: Shift + F
        keyboard.add_hotkey('shift+f', self.cancel_trade)
        
        # Exit trades: Shift + J, K, L
        keyboard.add_hotkey('shift+j', lambda: self.exit_trade('profit'))
        keyboard.add_hotkey('shift+k', lambda: self.exit_trade('loss'))
        keyboard.add_hotkey('shift+l', lambda: self.exit_trade('breakeven'))
        
        # Pause/Resume: Space
        keyboard.add_hotkey('space', self.toggle_pause)
    
    def candle_generation_loop(self):
        """Generate new candles every few seconds"""
        while self.running:
            if not self.paused:
                time.sleep(3)  # New candle every 3 seconds for practice
                new_candle = self.candlestick_gen.generate_candle()
                
                # Add to display list
                self.candles_display.append(new_candle)
                if len(self.candles_display) > self.max_candles_display:
                    self.candles_display.pop(0)
                
                # Check for breakout
                self.check_for_breakout()
                
                # Reset trade state for new candle
                self.current_candle_start_time = time.time()
                self.trade_entered = False
    
    def check_for_breakout(self):
        """Check if current candle breaks previous candle's high"""
        if len(self.candles_display) < 2:
            return
            
        current_candle = self.candles_display[-1]
        previous_candle = self.candles_display[-2]
        
        if current_candle['high'] > previous_candle['high']:
            if not self.breakout_detected:
                self.breakout_detected = True
                self.breakout_time = time.time()
                self.total_breakouts += 1
                print(f"Breakout detected! Current high: {current_candle['high']}, Previous high: {previous_candle['high']}")
    
    def enter_trade(self, trade_type: str):
        """Handle trade entry"""
        if self.breakout_detected and not self.trade_entered:
            self.trade_entered = True
            self.trade_entry_time = time.time()
            
            if self.breakout_time:
                reaction_time = (self.trade_entry_time - self.breakout_time) * 1000  # Convert to ms
                self.reaction_times.append(reaction_time)
                self.successful_entries += 1
                self.average_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
                
                print(f"Trade entered ({trade_type})! Reaction time: {reaction_time:.0f}ms")
        
        # Reset for next opportunity
        self.breakout_detected = False
        self.breakout_time = None
    
    def cancel_trade(self):
        """Cancel current trade setup"""
        self.trade_entered = False
        self.breakout_detected = False
        print("Trade cancelled!")
    
    def exit_trade(self, exit_type: str):
        """Handle trade exit"""
        if self.trade_entered:
            print(f"Trade exited: {exit_type}")
            self.trade_entered = False
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        print(f"Game {'paused' if self.paused else 'resumed'}")
    
    def draw_candlestick(self, x: int, y: int, width: int, height: int, candle: dict):
        """Draw a single candlestick"""
        open_price = candle['open']
        high_price = candle['high']
        low_price = candle['low']
        close_price = candle['close']
        
        # Determine color
        color = self.GREEN if close_price >= open_price else self.RED
        
        # Calculate positions based on price range
        if len(self.candles_display) > 1:
            all_highs = [c['high'] for c in self.candles_display]
            all_lows = [c['low'] for c in self.candles_display]
            price_range = max(all_highs) - min(all_lows)
            
            if price_range > 0:
                # Scale prices to fit chart height
                high_y = y + height - ((high_price - min(all_lows)) / price_range * height)
                low_y = y + height - ((low_price - min(all_lows)) / price_range * height)
                open_y = y + height - ((open_price - min(all_lows)) / price_range * height)
                close_y = y + height - ((close_price - min(all_lows)) / price_range * height)
                
                # Draw high-low line
                pygame.draw.line(self.screen, color, (x + width//2, high_y), (x + width//2, low_y), 2)
                
                # Draw body rectangle
                body_top = min(open_y, close_y)
                body_bottom = max(open_y, close_y)
                body_height = max(1, body_bottom - body_top)
                
                pygame.draw.rect(self.screen, color, (x, body_top, width, body_height))
    
    def draw_chart(self):
        """Draw the candlestick chart"""
        # Draw chart background
        pygame.draw.rect(self.screen, self.WHITE, (self.chart_x, self.chart_y, self.chart_width, self.chart_height))
        pygame.draw.rect(self.screen, self.BLACK, (self.chart_x, self.chart_y, self.chart_width, self.chart_height), 2)
        
        # Draw candles
        if self.candles_display:
            candle_width = self.chart_width // len(self.candles_display)
            
            for i, candle in enumerate(self.candles_display):
                x = self.chart_x + i * candle_width
                self.draw_candlestick(x + 1, self.chart_y, candle_width - 2, self.chart_height, candle)
        
        # Highlight if breakout is detected
        if self.breakout_detected:
            pygame.draw.rect(self.screen, self.BLUE, (self.chart_x, self.chart_y, self.chart_width, self.chart_height), 5)
    
    def draw_hud(self):
        """Draw heads-up display with stats and instructions"""
        hud_x = self.chart_x + self.chart_width + 20
        y_offset = 50
        
        # Title
        title = self.font_large.render("Scalp Trainer", True, self.BLACK)
        self.screen.blit(title, (hud_x, y_offset))
        y_offset += 60
        
        # Statistics
        stats_text = [
            f"Total Breakouts: {self.total_breakouts}",
            f"Successful Entries: {self.successful_entries}",
            f"Success Rate: {(self.successful_entries/max(1,self.total_breakouts)*100):.1f}%",
            f"Avg Reaction Time: {self.average_reaction_time:.0f}ms",
            "",
            "CONTROLS:",
            "Shift+A/S/D - Enter Trade",
            "Shift+F - Cancel Trade", 
            "Shift+J/K/L - Exit Trade",
            "Space - Pause/Resume",
            "",
            f"Status: {'PAUSED' if self.paused else 'RUNNING'}",
            f"Breakout: {'YES' if self.breakout_detected else 'NO'}",
            f"In Trade: {'YES' if self.trade_entered else 'NO'}"
        ]
        
        for text in stats_text:
            if text:  # Skip empty lines
                color = self.RED if text.startswith("Status: PAUSED") else self.BLACK
                color = self.GREEN if text.startswith("Breakout: YES") else color
                color = self.BLUE if text.startswith("In Trade: YES") else color
                
                rendered_text = self.font_small.render(text, True, color)
                self.screen.blit(rendered_text, (hud_x, y_offset))
            y_offset += 30
        
        # Current prices
        if self.candles_display:
            current = self.candles_display[-1]
            price_text = f"Current: O:{current['open']} H:{current['high']} L:{current['low']} C:{current['close']}"
            price_surface = self.font_medium.render(price_text, True, self.BLACK)
            self.screen.blit(price_surface, (self.chart_x, self.chart_y + self.chart_height + 20))
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Clear screen
            self.screen.fill(self.LIGHT_GRAY)
            
            # Draw everything
            self.draw_chart()
            self.draw_hud()
            
            # Update display
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    print("Starting Scalp Trading Trainer...")
    print("Controls:")
    print("  Shift+A/S/D - Enter different types of trades")
    print("  Shift+F - Cancel trade setup")
    print("  Shift+J/K/L - Exit trades (profit/loss/breakeven)")
    print("  Space - Pause/Resume")
    print("\nWatch for candles that break the previous candle's high!")
    print("Enter trades as quickly as possible when breakouts occur.")
    
    trainer = TradeScalpTrainer()
    trainer.run()