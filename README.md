# Scalp Trading Trainer

A Python application designed to help traders practice scalping trades based on candlestick formations. The primary focus is developing quick reaction times when entering trades based on breakout patterns.

## Features

- **Real-time Candlestick Chart**: Displays randomly generated OHLC candlestick data that updates every 3 seconds
- **Breakout Detection**: Automatically detects when the current candle breaks the previous candle's high
- **Reaction Time Tracking**: Measures and tracks your reaction time from breakout detection to trade entry
- **Performance Metrics**: Shows success rate, average reaction time, and total breakouts
- **Global Hotkeys**: Practice with keyboard shortcuts that work even when the window isn't in focus

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python scalp_trainer.py
```

## Controls

### Trade Entry (Shift + ASD)
- **Shift + A**: Enter Long Trade
- **Shift + S**: Enter Short Trade  
- **Shift + D**: Enter Breakout Trade

### Trade Management
- **Shift + F**: Cancel Trade Setup
- **Shift + J**: Exit Trade (Profit)
- **Shift + K**: Exit Trade (Loss)
- **Shift + L**: Exit Trade (Breakeven)

### App Controls
- **Space**: Pause/Resume the application

## How to Use

1. **Launch the App**: Run `python scalp_trainer.py`
2. **Watch for Breakouts**: The chart will highlight in blue when a breakout is detected
3. **React Quickly**: Press Shift+A, Shift+S, or Shift+D as fast as possible when you see a breakout
4. **Track Performance**: Monitor your reaction times and success rate in the right panel
5. **Practice**: The app runs continuously with new randomly generated data

## Game Mechanics

- **Breakout Definition**: When the current candle's high exceeds the previous candle's high
- **Scoring**: Reaction time is measured in milliseconds from breakout detection to key press
- **Success Rate**: Percentage of breakouts where you successfully entered a trade
- **Continuous Play**: Data loops automatically to provide endless practice

## Performance Tracking

The app tracks several key metrics:
- Total number of breakouts detected
- Successful trade entries
- Success rate percentage
- Average reaction time in milliseconds
- Individual reaction times for each successful entry

## Tips for Improvement

1. **Focus on the Chart**: Keep your eyes on the candlesticks, not the statistics
2. **Finger Position**: Keep your fingers hovering over the Shift+A/S/D keys
3. **Quick Decision**: Don't overthink - react to breakouts immediately
4. **Practice Regularly**: Consistent practice will improve your reaction times
5. **Use Peripheral Vision**: Try to notice breakouts in your peripheral vision

## Technical Notes

- New candles generate every 3 seconds (faster than real 1-minute candles for practice)
- Data is randomly generated with realistic price movements and trends
- The keyboard library allows global hotkeys that work system-wide
- Chart displays the last 50 candles with automatic scrolling

## Requirements

- Python 3.7+
- pygame 2.5.0+
- keyboard 0.13.5+
- pandas 2.0.0+
- numpy 1.24.0+
- matplotlib 3.7.0+

## Troubleshooting

**Hotkeys not working**: The app requires administrative privileges on some systems for global hotkeys to function properly.

**Performance issues**: Close other applications to ensure smooth 60 FPS performance.

**Chart not updating**: Check that the app isn't paused (press Space to resume).