# 🚨 Alert Testing Guide

This guide shows you how to test the automated alert system for genuine price changes in your AI Stock Tracking Agent.

## 📋 Overview

Your system has several ways to test automated alerts:

1. **Simulated Alerts** - Test with fake data (fastest)
2. **Real Stock Alerts** - Test with actual market data
3. **Background Scheduler** - Test the automated monitoring
4. **Threshold Testing** - Test different price change scenarios

## 🚀 Quick Start

### Option 1: Quick Test (Recommended for beginners)
```bash
# Activate your virtual environment
source venv/bin/activate

# Run the quick alert test
python3 quick_alert_test.py
```

This will:
- Test with simulated price changes
- Show you exactly what alerts look like
- Complete in under 30 seconds

### Option 2: Comprehensive Testing
```bash
# Run the full test suite
python3 test_alerts.py
```

This will:
- Test multiple scenarios
- Use real stock data
- Test the scheduler
- Show detailed results

### Option 3: Scheduler Testing
```bash
# Test the background monitoring system
python3 test_scheduler.py
```

This will:
- Start the background scheduler
- Simulate automatic stock monitoring
- Show how alerts are generated automatically

## 📊 Testing Scenarios

### 1. Simulated Price Changes

**What it tests:** Alert generation with fake data
**When to use:** Quick verification, offline testing
**Example:**
- Stock: TEST1
- Previous price: $100.00
- New price: $106.00 (+6% change)
- Result: Alert triggered (above 5% threshold)

### 2. Real Stock Data

**What it tests:** Alert generation with actual market data
**When to use:** During market hours, realistic testing
**Example:**
- Stock: AAPL (Apple)
- Current price: $150.00 (real)
- Simulated change: +6% to $159.00
- Result: Alert with real stock context

### 3. Background Scheduler

**What it tests:** Automated monitoring system
**When to use:** Testing the full automation
**Example:**
- Monitors: AAPL, TSLA, GOOGL, MSFT
- Checks every hour (configurable)
- Automatically sends alerts when thresholds exceeded

### 4. Threshold Testing

**What it tests:** Different price change scenarios
**When to use:** Verifying alert logic
**Examples:**
- 2% change: No alert (below 5% threshold)
- 5% change: Alert triggered (at threshold)
- 10% change: Alert triggered (well above threshold)

## 🎯 Alert Threshold Configuration

Your current settings:
- **Alert threshold:** 5% (configurable in `.env`)
- **Check interval:** 60 minutes (configurable in `.env`)

To change these settings, edit your `.env` file:
```bash
# Alert when stock moves 3% or more
ALERT_THRESHOLD_PERCENT=3.0

# Check stocks every 30 minutes
CHECK_INTERVAL_MINUTES=30
```

## 📱 What You'll See

When an alert is triggered, you'll see:

```
============================================================
📱 MOCK SMS SENT
To: +1555USER123
Message: 📈 AAPL Alert

Price: $157.50 (+5.00%)
Previous: $150.00

Apple Inc. (AAPL) has shown a significant price increase of 5.00%, 
moving from $150.00 to $157.50. This positive movement suggests 
strong investor confidence and potential market momentum.

Key factors:
• Strong quarterly earnings report
• Positive analyst upgrades
• Market sentiment improvement

📰 Recent news: Apple reports record Q4 revenue...
============================================================
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Could not fetch data for [SYMBOL]"**
   - **Cause:** Stock symbol doesn't exist or market is closed
   - **Solution:** Try a different symbol (AAPL, MSFT, GOOGL)

2. **"No alert triggered"**
   - **Cause:** Price change below threshold
   - **Solution:** Increase the change percentage in test

3. **"Error generating alert"**
   - **Cause:** OpenAI API key not set or invalid
   - **Solution:** Check your `.env` file has `OPENAI_API_KEY`

### Debug Mode:
```bash
# Enable debug logging
export DEBUG=true
python3 quick_alert_test.py
```

## 📈 Real-World Testing

### During Market Hours (9:30 AM - 4:00 PM EST):
```bash
# Test with real, live stock prices
python3 quick_alert_test.py
# Choose option 2: "Real stock test"
```

### After Market Hours:
```bash
# Test with simulated data
python3 quick_alert_test.py
# Choose option 1: "Simulated alert test"
```

## 🎛️ Advanced Testing

### Custom Stock Symbols:
Edit the test scripts to use different stocks:
```python
# In quick_alert_test.py, change:
symbol = "TSLA"  # Instead of "AAPL"
```

### Custom Price Changes:
```python
# Test different scenarios
previous_price = 100.00
current_price = 110.00  # 10% increase
# or
current_price = 95.00   # 5% decrease
```

### Multiple Stocks:
```python
# Test multiple stocks at once
test_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
```

## 📊 Expected Results

### Successful Test Output:
```
🚀 Quick Alert Test
========================================
🔄 Initializing services...
✅ All services initialized successfully!
📊 Testing alert for AAPL
💰 Price change: $150.00 → $157.50
📈 Change: +5.00%
🎯 Alert threshold: 5.0%
🚨 This change would trigger an alert!

🤖 Generating AI analysis...
✅ Analysis generated (confidence: 0.85)
📝 Creating alert message...
📱 Sending mock SMS alert...

============================================================
📱 MOCK SMS SENT
To: +1555USER123
Message: [Alert message content]
============================================================

✅ Alert test completed!
📋 Check the mock SMS output above to see what the user would receive.
```

## 🚀 Next Steps

After testing alerts:

1. **Configure real Twilio** (if you want real SMS)
2. **Adjust thresholds** based on your preferences
3. **Add more stocks** to your watchlist
4. **Set up production deployment**

## 💡 Tips

- **Start with simulated tests** - they're faster and more reliable
- **Test during market hours** for realistic data
- **Use the quick test** for rapid iteration
- **Check the mock SMS output** to see exactly what users receive
- **Adjust thresholds** based on your risk tolerance

## 🆘 Need Help?

If you encounter issues:
1. Check the error messages in the console
2. Verify your `.env` file has the required API keys
3. Try the simulated tests first (they don't need internet)
4. Check that your virtual environment is activated

Happy testing! 🎉
