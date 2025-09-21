import pygame
import numpy as np
import pandas as pd
import time
import threading
import keyboard
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

class SupportResistanceLevel:
    """Represents a support or resistance level"""
    def __init__(self, price: float, level_type: str, strength: int = 3):
        self.price = price
        self.type = level_type  # 'support' or 'resistance'
        self.strength = strength  # 1-5, higher = stronger
        self.touches = 0
        self.created_time = time.time()
        self.active = True

class CandlestickGenerator:
    """Generates realistic candlestick data with volume and S/R levels"""
    
    def __init__(self, initial_price: float = 100.0):
        self.current_price = initial_price
        self.trend = random.choice([1, -1])  # 1 for uptrend, -1 for downtrend
        self.trend_strength = random.uniform(0.1, 0.3)
        self.volatility = random.uniform(0.5, 2.0)
        self.candles = []
        
        # Volume parameters
        self.base_volume = 1000  # Base volume level
        self.volume_volatility = 0.3
        
        # Support/Resistance levels
        self.sr_levels = []
        self.price_range_history = [initial_price]
        self.initialize_sr_levels()
        
    def initialize_sr_levels(self):
        """Create initial support and resistance levels"""
        price_range = self.current_price * 0.1  # 10% range around current price
        
        # Create 4-6 S/R levels
        num_levels = random.randint(4, 6)
        for _ in range(num_levels):
            level_price = self.current_price + random.uniform(-price_range, price_range)
            level_type = 'support' if level_price < self.current_price else 'resistance'
            strength = random.randint(2, 5)
            
            sr_level = SupportResistanceLevel(level_price, level_type, strength)
            self.sr_levels.append(sr_level)
        
        # Sort by price for easier management
        self.sr_levels.sort(key=lambda x: x.price)
    
    def update_sr_levels(self):
        """Manage support/resistance levels dynamically"""
        # Remove old levels (older than 100 candles)
        current_time = time.time()
        self.sr_levels = [level for level in self.sr_levels 
                         if level.active and (current_time - level.created_time) < 300]
        
        # Occasionally add new levels
        if random.random() < 0.1 and len(self.sr_levels) < 8:  # 10% chance, max 8 levels
            price_range = max(self.price_range_history) - min(self.price_range_history)
            if price_range > 0:
                level_price = random.uniform(min(self.price_range_history), max(self.price_range_history))
                level_type = 'support' if level_price < self.current_price else 'resistance'
                strength = random.randint(2, 4)
                
                sr_level = SupportResistanceLevel(level_price, level_type, strength)
                self.sr_levels.append(sr_level)
                self.sr_levels.sort(key=lambda x: x.price)
    
    def calculate_sr_influence(self, target_price: float) -> Tuple[float, float]:
        """Calculate how nearby S/R levels influence price movement and volume"""
        price_influence = 0.0
        volume_multiplier = 1.0
        
        for level in self.sr_levels:
            if not level.active:
                continue
                
            distance = abs(target_price - level.price)
            max_influence_distance = self.current_price * 0.02  # 2% of current price
            
            if distance < max_influence_distance:
                # Calculate influence strength based on distance and level strength
                influence_strength = (1 - distance / max_influence_distance) * level.strength * 0.1
                
                # Price influence: resistance pushes down, support pushes up
                if level.type == 'resistance' and target_price > level.price:
                    price_influence -= influence_strength
                elif level.type == 'support' and target_price < level.price:
                    price_influence += influence_strength
                
                # Volume increase near levels
                volume_multiplier += influence_strength * 2
                
                # Mark level as touched
                if distance < self.current_price * 0.005:  # Very close touch
                    level.touches += 1
        
        return price_influence, min(volume_multiplier, 5.0)  # Cap volume multiplier
    
    def generate_volume(self, candle_data: dict, volume_multiplier: float = 1.0) -> int:
        """Generate realistic volume based on price action"""
        # Base volume with random variation
        volume = self.base_volume * random.uniform(0.5, 1.5)
        
        # Volume correlates with candle size (range)
        candle_range = candle_data['high'] - candle_data['low']
        avg_range = self.volatility
        if avg_range > 0:
            range_multiplier = 1 + (candle_range / avg_range - 1) * 0.5
            volume *= max(0.3, range_multiplier)
        
        # Higher volume on trend moves
        if abs(candle_data['close'] - candle_data['open']) > avg_range * 0.5:
            volume *= 1.5
        
        # Apply S/R influence
        volume *= volume_multiplier
        
        # Add random variation
        volume *= random.uniform(0.8, 1.2)
        
        return int(max(100, volume))  # Minimum volume of 100
        
    def generate_candle(self) -> dict:
        """Generate a single candlestick with S/R influence and volume"""
        # Update S/R levels management
        self.update_sr_levels()
        
        # Add some trend and randomness
        base_move = self.trend * self.trend_strength * random.uniform(0.5, 1.5)
        random_move = random.uniform(-self.volatility, self.volatility)
        
        open_price = self.current_price
        target_close = open_price + base_move + random_move
        
        # Apply S/R influence to the target close price
        sr_influence, volume_multiplier = self.calculate_sr_influence(target_close)
        close_price = target_close + sr_influence
        
        # Generate high and low with S/R influence
        base_high = max(open_price, close_price) + random.uniform(0, self.volatility * 0.5)
        base_low = min(open_price, close_price) - random.uniform(0, self.volatility * 0.5)
        
        # Apply S/R influence to high/low
        high_sr_influence, _ = self.calculate_sr_influence(base_high)
        low_sr_influence, _ = self.calculate_sr_influence(base_low)
        
        high_price = base_high + high_sr_influence
        low_price = base_low + low_sr_influence
        
        # Ensure price integrity (high >= max(open,close), low <= min(open,close))
        high_price = max(high_price, max(open_price, close_price))
        low_price = min(low_price, min(open_price, close_price))
        
        # Occasionally change trend (less likely near strong S/R levels)
        trend_change_probability = 0.05
        if volume_multiplier > 2.0:  # Near strong S/R level
            trend_change_probability *= 0.5  # Reduce trend change probability
        
        if random.random() < trend_change_probability:
            self.trend *= -1
            self.trend_strength = random.uniform(0.1, 0.3)
            self.volatility = random.uniform(0.5, 2.0)
        
        # Create candle data structure
        candle_data = {
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'timestamp': datetime.now()
        }
        
        # Generate volume based on price action and S/R influence
        volume = self.generate_volume(candle_data, volume_multiplier)
        candle_data['volume'] = volume
        
        # Update current price and price history
        self.current_price = close_price
        self.price_range_history.append(close_price)
        if len(self.price_range_history) > 100:  # Keep last 100 prices
            self.price_range_history.pop(0)
        
        self.candles.append(candle_data)
        return candle_data

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
        self.font_tiny = pygame.font.Font(None, 18)  # For S/R labels
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
        self.trade_entry_price = None
        self.reaction_times = []
        
        # Performance tracking
        self.total_breakouts = 0
        self.total_trades = 0
        self.successful_trades = 0  # Based on exit button pressed
        self.score_wins = 0  # Based on actual price movement (+1 score)
        self.average_reaction_time = 0
        self.cumulative_score = 0  # Running score based on trade outcomes
        
        # Chart settings
        self.chart_x = 70  # Moved right to make room for S/R labels
        self.chart_y = 80   # Moved down to use more screen space
        self.chart_width = 800
        self.chart_height = 450  # Increased height for better chart visibility
        self.chart_padding = 20  # Padding for candlesticks at edges
        
        # Volume chart settings
        self.volume_height = 120  # Slightly increased volume chart height
        self.volume_y = self.chart_y + self.chart_height  # Remove gap, connect directly
        
        # Colors for S/R levels
        self.SUPPORT_COLOR = (0, 128, 0)  # Dark green
        self.RESISTANCE_COLOR = (128, 0, 0)  # Dark red
        self.LEVEL_WEAK = (150, 150, 150)  # Light gray for weak levels
        
        # Generate initial candles
        for _ in range(self.max_candles_display):
            self.candles_display.append(self.candlestick_gen.generate_candle())
        
        # Store max volume for scaling
        self.max_volume = max([c.get('volume', 1000) for c in self.candles_display])
        
        # Start the candle generation thread
        self.candle_thread = threading.Thread(target=self.candle_generation_loop, daemon=True)
        self.candle_thread.start()
        
        # Debug mode for testing (allows trades anytime)
        self.debug_mode = True  # Set to False for normal operation
        
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
        
        # Reset statistics: Shift + R
        keyboard.add_hotkey('shift+r', self.reset_statistics)
        
        # Exit application: Escape
        keyboard.add_hotkey('esc', self.exit_application)
        
        # Toggle debug mode: Shift + T
        keyboard.add_hotkey('shift+t', self.toggle_debug_mode)
    
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
                
                # Update max volume for scaling
                current_volumes = [c.get('volume', 1000) for c in self.candles_display]
                self.max_volume = max(current_volumes)
                
                # Check for breakout
                self.check_for_breakout()
                
                # Update candle timing (but don't reset trade state)
                self.current_candle_start_time = time.time()
    
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
        # In debug mode, always allow trades (except when already in trade)
        if not self.trade_entered:
            self.trade_entered = True
            self.trade_entry_time = time.time()
            
            # Set trade entry price to current candle's close
            if self.candles_display:
                self.trade_entry_price = self.candles_display[-1]['close']
            
            if self.breakout_time and not self.debug_mode:
                reaction_time = (self.trade_entry_time - self.breakout_time) * 1000  # Convert to ms
                self.reaction_times.append(reaction_time)
                self.average_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
                print(f"Trade entered ({trade_type})! Reaction time: {reaction_time:.0f}ms")
            else:
                print(f"Trade entered ({trade_type})! Entry price: {self.trade_entry_price:.2f}")
        else:
            print(f"Cannot enter trade - already in trade! Exit current trade first.")
        
        # Reset breakout for next opportunity
        self.breakout_detected = False
        self.breakout_time = None
    
    def cancel_trade(self):
        """Cancel current trade setup"""
        self.trade_entered = False
        self.trade_entry_price = None
        self.breakout_detected = False
        print("Trade cancelled!")
    
    def exit_trade(self, exit_type: str):
        """Handle trade exit"""
        if self.trade_entered and self.trade_entry_price and self.candles_display:
            self.total_trades += 1
            current_price = self.candles_display[-1]['close']
            
            # Calculate score based on trade outcome relative to entry price
            if exit_type == 'profit':
                self.successful_trades += 1
                if current_price > self.trade_entry_price:
                    self.cumulative_score += 1
                    self.score_wins += 1
                    score_change = "+1"
                elif current_price < self.trade_entry_price:
                    self.cumulative_score -= 1
                    score_change = "-1"
                else:
                    score_change = "0"
            elif exit_type == 'loss':
                if current_price < self.trade_entry_price:
                    self.cumulative_score -= 1
                    score_change = "-1"
                elif current_price > self.trade_entry_price:
                    self.cumulative_score += 1
                    self.score_wins += 1
                    score_change = "+1"
                else:
                    score_change = "0"
            else:  # breakeven
                score_change = "0"
            
            print(f"Trade exited: {exit_type} | Entry: {self.trade_entry_price:.2f} | Exit: {current_price:.2f} | Score: {score_change} | Total: {self.cumulative_score}")
            self.trade_entered = False
            self.trade_entry_price = None
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        print(f"Game {'paused' if self.paused else 'resumed'}")
    
    def reset_statistics(self):
        """Reset all performance statistics"""
        self.total_breakouts = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.score_wins = 0
        self.average_reaction_time = 0
        self.cumulative_score = 0
        self.reaction_times = []
        print("Statistics reset! Starting fresh.")
    
    def toggle_debug_mode(self):
        """Toggle debug mode for easier testing"""
        self.debug_mode = not self.debug_mode
        mode_text = "ON (trade anytime)" if self.debug_mode else "OFF (breakouts only)"
        print(f"Debug mode: {mode_text}")
    
    def exit_application(self):
        """Exit the application cleanly"""
        print(f"Exiting application... Final Score: {self.cumulative_score}")
        self.running = False
    
    def draw_candlestick(self, x: int, y: int, width: int, height: int, candle: dict):
        """Draw a single candlestick"""
        open_price = candle['open']
        high_price = candle['high']
        low_price = candle['low']
        close_price = candle['close']
        
        # Determine color
        color = self.GREEN if close_price >= open_price else self.RED
        
        # Calculate positions based on price range with padding
        if len(self.candles_display) > 1:
            all_highs = [c['high'] for c in self.candles_display]
            all_lows = [c['low'] for c in self.candles_display]
            price_range = max(all_highs) - min(all_lows)
            
            if price_range > 0:
                # Add padding to price range for better visualization
                price_min = min(all_lows)
                price_max = max(all_highs)
                padding = price_range * 0.05  # 5% padding on top and bottom
                
                adjusted_min = price_min - padding
                adjusted_max = price_max + padding
                adjusted_range = adjusted_max - adjusted_min
                
                # Scale prices to fit chart height with padding
                usable_height = height - (2 * self.chart_padding)
                
                high_y = y + self.chart_padding + usable_height - ((high_price - adjusted_min) / adjusted_range * usable_height)
                low_y = y + self.chart_padding + usable_height - ((low_price - adjusted_min) / adjusted_range * usable_height)
                open_y = y + self.chart_padding + usable_height - ((open_price - adjusted_min) / adjusted_range * usable_height)
                close_y = y + self.chart_padding + usable_height - ((close_price - adjusted_min) / adjusted_range * usable_height)
                
                # Draw high-low line
                pygame.draw.line(self.screen, color, (x + width//2, high_y), (x + width//2, low_y), 2)
                
                # Draw body rectangle
                body_top = min(open_y, close_y)
                body_bottom = max(open_y, close_y)
                body_height = max(1, body_bottom - body_top)
                
                pygame.draw.rect(self.screen, color, (x, body_top, width, body_height))
    
    def draw_chart(self):
        """Draw the candlestick chart with S/R levels and volume"""
        # Draw chart background
        pygame.draw.rect(self.screen, self.WHITE, (self.chart_x, self.chart_y, self.chart_width, self.chart_height))
        pygame.draw.rect(self.screen, self.BLACK, (self.chart_x, self.chart_y, self.chart_width, self.chart_height), 2)
        
        # Draw Support/Resistance levels first (behind candles)
        self.draw_sr_levels()
        
        # Draw candles with proper spacing
        if self.candles_display:
            candle_width = (self.chart_width - 2 * self.chart_padding) // len(self.candles_display)
            
            for i, candle in enumerate(self.candles_display):
                x = self.chart_x + self.chart_padding + i * candle_width
                self.draw_candlestick(x + 1, self.chart_y, candle_width - 2, self.chart_height, candle)
        
        # Draw volume bars
        self.draw_volume_bars()
        
        # Draw trade entry line if in trade
        if self.trade_entered and self.trade_entry_price and self.candles_display:
            self.draw_trade_line()
        
        # Highlight if breakout is detected
        if self.breakout_detected:
            pygame.draw.rect(self.screen, self.BLUE, (self.chart_x, self.chart_y, self.chart_width, self.chart_height), 5)
    
    def draw_sr_levels(self):
        """Draw support and resistance levels"""
        if not self.candles_display:
            return
            
        # Get price range for scaling
        all_highs = [c['high'] for c in self.candles_display]
        all_lows = [c['low'] for c in self.candles_display]
        price_range = max(all_highs) - min(all_lows)
        
        if price_range > 0:
            price_min = min(all_lows)
            price_max = max(all_highs)
            padding = price_range * 0.05
            
            adjusted_min = price_min - padding
            adjusted_max = price_max + padding
            adjusted_range = adjusted_max - adjusted_min
            usable_height = self.chart_height - (2 * self.chart_padding)
            
            # Draw each S/R level
            for level in self.candlestick_gen.sr_levels:
                if not level.active:
                    continue
                    
                # Only draw levels within visible price range
                if adjusted_min <= level.price <= adjusted_max:
                    # Calculate Y position
                    level_y = self.chart_y + self.chart_padding + usable_height - ((level.price - adjusted_min) / adjusted_range * usable_height)
                    
                    # Choose color and thickness based on type and strength
                    if level.type == 'support':
                        color = self.SUPPORT_COLOR
                    else:
                        color = self.RESISTANCE_COLOR
                    
                    # Weaker levels are lighter and thinner
                    if level.strength < 3:
                        color = self.LEVEL_WEAK
                        thickness = 1
                    else:
                        thickness = min(level.strength - 1, 3)  # Max thickness of 3
                    
                    # Draw the level line
                    pygame.draw.line(self.screen, color, 
                                   (self.chart_x, level_y), 
                                   (self.chart_x + self.chart_width, level_y), 
                                   thickness)
                    
                    # Draw price label on the left side with smaller font
                    label_text = f"{level.price:.2f}"
                    label_surface = self.font_tiny.render(label_text, True, color)
                    self.screen.blit(label_surface, (self.chart_x - 45, level_y - 8))
    
    def draw_volume_bars(self):
        """Draw volume bars below the chart"""
        if not self.candles_display:
            return
            
        # Draw volume chart background
        volume_rect = (self.chart_x, self.volume_y, self.chart_width, self.volume_height)
        pygame.draw.rect(self.screen, self.WHITE, volume_rect)
        pygame.draw.rect(self.screen, self.BLACK, volume_rect, 2)
        
        # Draw volume bars
        candle_width = (self.chart_width - 2 * self.chart_padding) // len(self.candles_display)
        
        for i, candle in enumerate(self.candles_display):
            volume = candle.get('volume', 1000)
            
            # Calculate bar height based on volume (reduced scale)
            if self.max_volume > 0:
                bar_height = (volume / self.max_volume) * (self.volume_height - 30) * 0.6  # 30px padding, 60% scale
            else:
                bar_height = 0
            
            # Position and size
            x = self.chart_x + self.chart_padding + i * candle_width + 1
            bar_width = candle_width - 2
            bar_y = self.volume_y + self.volume_height - bar_height - 15  # 15px bottom padding
            
            # Color based on price movement (green for up, red for down)
            if candle['close'] >= candle['open']:
                color = self.GREEN
            else:
                color = self.RED
            
            # Draw volume bar
            if bar_height > 1:
                pygame.draw.rect(self.screen, color, (x, bar_y, bar_width, bar_height))
        
        # Draw volume scale labels on the left
        if self.max_volume > 0:
            # Max volume label
            max_vol_text = f"{int(self.max_volume):,}"
            max_vol_surface = self.font_tiny.render(max_vol_text, True, self.BLACK)
            self.screen.blit(max_vol_surface, (self.chart_x - 45, self.volume_y + 5))
            
            # Half volume label
            half_vol_text = f"{int(self.max_volume/2):,}"
            half_vol_surface = self.font_tiny.render(half_vol_text, True, self.BLACK)
            self.screen.blit(half_vol_surface, (self.chart_x - 45, self.volume_y + self.volume_height//2))
    
    def draw_trade_line(self):
        """Draw horizontal line showing trade entry price"""
        if not self.trade_entry_price or not self.candles_display:
            return
            
        # Calculate price range with same logic as candlesticks
        all_highs = [c['high'] for c in self.candles_display]
        all_lows = [c['low'] for c in self.candles_display]
        price_range = max(all_highs) - min(all_lows)
        
        if price_range > 0:
            # Add padding to price range for consistency
            price_min = min(all_lows)
            price_max = max(all_highs)
            padding = price_range * 0.05
            
            adjusted_min = price_min - padding
            adjusted_max = price_max + padding
            adjusted_range = adjusted_max - adjusted_min
            
            # Calculate Y position for trade entry price
            usable_height = self.chart_height - (2 * self.chart_padding)
            trade_line_y = self.chart_y + self.chart_padding + usable_height - ((self.trade_entry_price - adjusted_min) / adjusted_range * usable_height)
            
            # Draw horizontal line across the chart
            pygame.draw.line(self.screen, self.BLUE, 
                           (self.chart_x, trade_line_y), 
                           (self.chart_x + self.chart_width, trade_line_y), 3)
            
            # Draw price label
            price_label = self.font_small.render(f"Entry: {self.trade_entry_price:.2f}", True, self.BLUE)
            self.screen.blit(price_label, (self.chart_x + self.chart_width - 120, trade_line_y - 15))
    
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
            f"Total Trades: {self.total_trades}",
            f"Profitable Trades: {self.successful_trades}",
            f"Success Rate: {(self.successful_trades/max(1,self.total_trades)*100):.1f}%",
            f"Avg Reaction Time: {self.average_reaction_time:.0f}ms",
            "",
            "CONTROLS:",
            "Shift+A/S/D - Enter Trade",
            "Shift+F - Cancel Trade", 
            "Shift+J/K/L - Exit Trade",
            "Shift+R - Reset Stats",
            "Shift+T - Toggle Debug Mode",
            "Space - Pause/Resume",
            "ESC - Exit Game",
            "",
            f"Status: {'PAUSED' if self.paused else 'RUNNING'}",
            f"Debug Mode: {'ON' if self.debug_mode else 'OFF'}",
            f"Breakout: {'YES' if self.breakout_detected else 'NO'}",
            f"In Trade: {'YES' if self.trade_entered else 'NO'}"
        ]
        
        for text in stats_text:
            if text:  # Skip empty lines
                color = self.BLACK
                if text.startswith("Status: PAUSED"):
                    color = self.RED
                elif text.startswith("Breakout: YES"):
                    color = self.BLACK
                elif text.startswith("In Trade: YES"):
                    color = self.BLUE
                
                rendered_text = self.font_small.render(text, True, color)
                self.screen.blit(rendered_text, (hud_x, y_offset))
            y_offset += 30
        
        # Current prices (moved below volume chart)
        if self.candles_display:
            current = self.candles_display[-1]
            volume_text = f"Vol: {current.get('volume', 1000):,}"
            price_text = f"Current: O:{current['open']} H:{current['high']} L:{current['low']} C:{current['close']} | {volume_text}"
            price_surface = self.font_medium.render(price_text, True, self.BLACK)
            self.screen.blit(price_surface, (self.chart_x, self.volume_y + self.volume_height + 20))
            
            # Score summary row at bottom
            score_sign = "+" if self.cumulative_score > 0 else ""
            win_rate = (self.score_wins/max(1,self.total_trades)*100) if self.total_trades > 0 else 0
            bottom_text = f"Score: {score_sign}{self.cumulative_score} | Total: {self.total_trades} | Percent: {win_rate:.0f}%"
            bottom_surface = self.font_small.render(bottom_text, True, self.BLACK)
            self.screen.blit(bottom_surface, (self.chart_x, self.volume_y + self.volume_height + 55))
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Backup keyboard controls (when window has focus)
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        if event.key == pygame.K_a:
                            self.enter_trade('long')
                        elif event.key == pygame.K_s:
                            self.enter_trade('short')
                        elif event.key == pygame.K_d:
                            self.enter_trade('breakout')
                        elif event.key == pygame.K_f:
                            self.cancel_trade()
                        elif event.key == pygame.K_j:
                            self.exit_trade('profit')
                        elif event.key == pygame.K_k:
                            self.exit_trade('loss')
                        elif event.key == pygame.K_l:
                            self.exit_trade('breakeven')
                        elif event.key == pygame.K_r:
                            self.reset_statistics()
                        elif event.key == pygame.K_t:
                            self.toggle_debug_mode()
                    elif event.key == pygame.K_SPACE:
                        self.toggle_pause()
                    elif event.key == pygame.K_ESCAPE:
                        self.exit_application()
            
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
    print("Controls (Global hotkeys - work anywhere):")
    print("  Shift+A/S/D - Enter different types of trades")
    print("  Shift+F - Cancel trade setup")
    print("  Shift+J/K/L - Exit trades (profit/loss/breakeven)")
    print("  Shift+R - Reset statistics")
    print("  Shift+T - Toggle debug mode (trade anytime vs breakouts only)")
    print("  Space - Pause/Resume")
    print("  ESC - Exit application")
    print("\nIf global hotkeys don't work, click the game window and use the same keys.")
    print("\nStarting in DEBUG MODE - you can trade anytime!")
    print("Use Shift+T to toggle between debug and normal mode.")
    print("In normal mode: Wait for breakouts to practice reaction time.")
    
    trainer = TradeScalpTrainer()
    trainer.run()