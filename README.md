# Scalp Trading Trainer

A comprehensive Python application designed to help traders practice scalping trades with realistic market conditions. Features advanced candlestick analysis, support/resistance levels, volume confirmation, and precise trade execution timing.

## 🚀 Core Features

### **📊 Advanced Chart Analysis**
- **Real-time Candlestick Chart**: Displays realistic OHLC candlestick data with proper price continuity
- **Volume Bars**: Color-coded volume bars below the chart showing market participation
- **Support & Resistance Levels**: Dynamic horizontal levels that influence price action
- **Trade Entry Lines**: Visual horizontal lines showing your exact entry prices
- **Breakout Detection**: Automatically detects when candles break previous highs

### **🎯 Realistic Market Behavior**
- **Price Reactions at S/R Levels**: Price tends to bounce/reverse at key levels with increased volume
- **Volume-Price Correlation**: Higher volume on larger price moves and at key levels
- **Market Structure**: Support becomes resistance after breaks, realistic trend changes
- **Breakout Confirmation**: Volume spikes during genuine breakouts vs fake-outs

### **⚡ Performance Tracking**
- **Cumulative Scoring System**: Real-time +1/-1 scoring based on entry vs exit prices
- **Reaction Time Measurement**: Tracks millisecond precision for breakout responses  
- **Win Rate Analysis**: Percentage of profitable trades vs total trades
- **Trade Statistics**: Complete performance metrics and historical data

## 🛠 Installation

1. **Clone or download the repository**
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python scalp_trainer.py
```

4. **For Windows users:** If global hotkeys don't work, run as Administrator or use window-focused controls (click the game window first).

## 🎮 Controls

### **Trade Execution (Works Globally or Window-Focused)**
- **Shift + A**: Enter Long Trade
- **Shift + S**: Enter Short Trade  
- **Shift + D**: Enter Breakout Trade
- **Shift + F**: Cancel Trade Setup

### **Trade Management**
- **Shift + J**: Exit Trade (Profit) - Marks as winning trade
- **Shift + K**: Exit Trade (Loss) - Marks as losing trade  
- **Shift + L**: Exit Trade (Breakeven) - Neutral exit

### **Application Controls**
- **Shift + R**: Reset All Statistics
- **Shift + T**: Toggle Debug Mode (Trade Anytime vs Breakouts Only)
- **Space**: Pause/Resume Chart Updates
- **ESC**: Exit Application

### **Backup Controls**
If global hotkeys don't work, click the game window and use the same key combinations.

## 🎯 How to Use

### **Getting Started**
1. **Launch the App**: Run `python scalp_trainer.py`
2. **Choose Mode**: 
   - **Debug Mode (Default)**: Trade anytime for practice
   - **Normal Mode**: Only trade during breakouts (press Shift+T to toggle)

### **Trading Practice**
3. **Watch the Chart**: Observe candlesticks, volume bars, and support/resistance levels
4. **Enter Trades**: Use Shift+A/S/D when you see opportunities
5. **Manage Trades**: Exit with Shift+J (profit), Shift+K (loss), or Shift+L (breakeven)
6. **Monitor Performance**: Track your cumulative score and win percentage

### **Advanced Features**
- **Support/Resistance**: Price labels on left, watch for bounces and breakouts
- **Volume Confirmation**: Higher volume bars indicate stronger moves
- **Entry Lines**: Blue horizontal lines show your exact entry prices
- **Real-time Scoring**: +1 for profitable exits, -1 for losses

## 🎲 Game Mechanics

### **Scoring System**
- **Entry Price vs Exit Price**: Compare your exit price to entry price
- **+1 Point**: Exit price higher than entry (profitable)
- **-1 Point**: Exit price lower than entry (loss)
- **0 Points**: Exit price equal to entry (breakeven)
- **Cumulative Score**: Running total displayed prominently

### **Market Simulation**
- **Support/Resistance**: 4-6 dynamic levels influence price movement
- **Volume Reactions**: Higher volume near S/R levels and breakouts
- **Price Behavior**: Realistic bounces, breakouts, and trend changes
- **Continuous Data**: Endless stream of realistic market conditions

## 📈 Performance Tracking

### **Real-Time Metrics**
- **Cumulative Score**: Your running profit/loss score
- **Win Percentage**: Percentage of profitable trades vs total trades
- **Total Trades**: Number of completed trades (entry + exit)
- **Reaction Time**: Speed of trade entry during breakouts (normal mode)
- **Breakout Detection**: Total breakout opportunities identified

### **Visual Feedback**
- **Score Display**: Prominently shown at bottom of screen
- **Color Coding**: Green for profits, red for losses in various indicators
- **Trade Lines**: Visual confirmation of entry prices on chart
- **Volume Analysis**: See volume spikes during your trades

## 💡 Tips for Improvement

### **Trading Skills**
1. **Support/Resistance**: Watch for price reactions at horizontal lines
2. **Volume Confirmation**: Look for volume spikes during breakouts
3. **Entry Timing**: Enter trades at key levels for better risk/reward
4. **Exit Strategy**: Use Shift+J for profits when price moves favorably

### **Reaction Training**
5. **Finger Position**: Keep fingers ready on Shift+A/S/D keys
6. **Focus Training**: Watch candlesticks and volume simultaneously
7. **Pattern Recognition**: Notice support becoming resistance after breaks
8. **Peripheral Vision**: Develop ability to spot breakouts quickly

### **Performance Optimization**
9. **Debug Mode**: Use for unlimited practice without breakout restrictions
10. **Reset Stats**: Use Shift+R to start fresh practice sessions
11. **Track Progress**: Monitor win percentage improvement over time

## 🔧 Technical Details

### **Chart Engine**
- **Candle Generation**: New candles every 3 seconds with realistic OHLC data
- **Price Continuity**: Each candle opens where previous candle closed
- **Support/Resistance**: 4-6 dynamic levels with realistic price influence
- **Volume Simulation**: Correlated with price movement and S/R interactions

### **Performance Features**
- **Real-time Updates**: 60 FPS smooth chart updates
- **Global Hotkeys**: System-wide keyboard shortcuts via keyboard library
- **Window Backup**: Pygame event handling if global hotkeys fail
- **Memory Management**: Rolling 50-candle display with automatic cleanup

### **Market Realism**
- **S/R Behavior**: Price tends to bounce at levels, volume increases
- **Breakout Simulation**: Higher volume on genuine breaks vs fake-outs
- **Trend Changes**: Natural market rhythm with periodic trend shifts

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