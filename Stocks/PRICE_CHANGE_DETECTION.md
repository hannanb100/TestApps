# 📊 How Price Change Detection Works

This document explains exactly how the AI Stock Tracking Agent detects price changes and triggers alerts.

## 🔍 **Two Methods of Price Change Detection**

The app uses **both** methods depending on the context:

### **1. 🌐 Real-Time Website Data (Primary Method)**

**How it works:**
- Fetches **live stock prices** from **Yahoo Finance** using the `yfinance` library
- Gets the **current market price** and **previous close price** from the website
- Calculates the percentage change: `(current_price - previous_close) / previous_close * 100`

**Code location:** `app/services/stock_service.py`
```python
# Fetches live data from Yahoo Finance
ticker = yf.Ticker(symbol)
info = ticker.info
current_price = info.get('currentPrice')
previous_close = info.get('previousClose')
change_percent = ((current_price - previous_close) / previous_close) * 100
```

**Advantages:**
- ✅ Always gets the most current market price
- ✅ Works with any stock symbol
- ✅ No need to store previous prices
- ✅ Yahoo Finance provides reliable, real-time data

**When it's used:**
- When you manually check a stock price
- During scheduled price checks
- When testing the alert system

### **2. 💾 Stored Previous Prices (For Tracking)**

**How it works:**
- Stores the **last known price** for each tracked stock in the database
- Compares **current price** (from website) with **stored previous price**
- Calculates change: `(current_price - stored_previous_price) / stored_previous_price * 100`

**Code location:** `app/models/stock.py` (Stock model)
```python
class Stock(BaseModel):
    current_price: Optional[Decimal] = Field(None, description="Current stock price")
    previous_price: Optional[Decimal] = Field(None, description="Previous recorded price")
    last_checked: Optional[datetime] = Field(None, description="Last time price was checked")
```

**Advantages:**
- ✅ Tracks changes since you started monitoring
- ✅ Can detect trends over time
- ✅ More personalized to your tracking period

**When it's used:**
- For stocks you've added to your watchlist
- For long-term trend analysis
- For personalized alerts based on your tracking period

## ⏰ **How the Scheduler Works**

The background scheduler runs automatically and:

1. **Every hour** (configurable), it:
   - Gets list of tracked stocks from database
   - Fetches current prices from Yahoo Finance
   - Compares with stored previous prices
   - Triggers alerts if change exceeds threshold

2. **The process:**
   ```python
   # 1. Get current price from website
   current_price = await stock_service.get_stock_quote(symbol)
   
   # 2. Get stored previous price from database
   previous_price = stock.previous_price
   
   # 3. Calculate change
   change_percent = ((current_price - previous_price) / previous_price) * 100
   
   # 4. Check if alert needed
   if abs(change_percent) >= threshold:
       # Send alert!
   ```

## 🎯 **Which Method is Used When?**

### **For New Stocks (First Time):**
- Uses **website data** (current vs previous close)
- No stored history yet

### **For Tracked Stocks:**
- Uses **stored previous price** vs **current website price**
- Builds your personal tracking history

### **For Manual Checks:**
- Always uses **website data** for immediate results

## 📱 **Example Alert Scenarios**

### **Scenario 1: New Stock Alert**
```
You add AAPL to watchlist at $150.00
Scheduler runs 1 hour later:
- Current price from Yahoo: $157.50
- Previous close from Yahoo: $150.00
- Change: +5.00% (triggers alert)
```

### **Scenario 2: Tracked Stock Alert**
```
AAPL in your watchlist:
- Stored previous price: $150.00 (from last check)
- Current price from Yahoo: $157.50
- Change: +5.00% (triggers alert)
```

## 🔧 **Configuration**

You can control how often prices are checked:

```bash
# In your .env file
CHECK_INTERVAL_MINUTES=60    # Check every 60 minutes
ALERT_THRESHOLD_PERCENT=5.0  # Alert if price changes 5% or more
```

## 🚀 **Real-Time vs Batch Processing**

### **Real-Time (Immediate):**
- When you manually request a stock price
- When testing the system
- Uses website data for instant results

### **Batch Processing (Scheduled):**
- Background scheduler runs every hour
- Checks all tracked stocks at once
- Compares with stored previous prices
- Sends alerts for significant changes

## 💡 **Key Points**

1. **Primary data source:** Yahoo Finance (real-time website data)
2. **Price comparison:** Current website price vs stored previous price
3. **Alert trigger:** When change exceeds your threshold
4. **Scheduling:** Automatic checks every hour (configurable)
5. **Storage:** Previous prices stored in database for tracking

## 🔍 **Data Flow Summary**

```
1. Scheduler starts (every hour)
   ↓
2. Get list of tracked stocks from database
   ↓
3. For each stock:
   a. Fetch current price from Yahoo Finance
   b. Get stored previous price from database
   c. Calculate percentage change
   d. If change > threshold: Send alert
   ↓
4. Update stored prices in database
   ↓
5. Wait for next scheduled run
```

This hybrid approach gives you both **real-time accuracy** (from the website) and **personalized tracking** (from your stored history)!
