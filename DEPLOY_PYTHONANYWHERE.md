# Deploying BTST Strategy Bot on PythonAnywhere

This guide walks you through deploying the BTST bot on PythonAnywhere as an "Always-On" task.

---

## Prerequisites

- PythonAnywhere account (Free tier works, but paid tier recommended for Always-On tasks)
- GitHub repository with your bot code (optional but recommended)
- All API credentials ready (Angel One, Telegram, Delta Exchange)

---

## Step 1: Upload Your Code to PythonAnywhere

### Option A: Using Git (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   cd c:\Users\ronad\OneDrive\Desktop\TradingStrategies\btst-strategy
   git init
   git add .
   git commit -m "Initial BTST bot commit"
   git remote add origin https://github.com/YOUR_USERNAME/btst-strategy.git
   git push -u origin main
   ```

2. **Clone on PythonAnywhere**:
   - Log in to [PythonAnywhere](https://www.pythonanywhere.com)
   - Go to **Consoles** → **Bash**
   - Run:
     ```bash
     git clone https://github.com/YOUR_USERNAME/btst-strategy.git
     cd btst-strategy
     ```

### Option B: Upload Files Manually

1. Go to **Files** tab in PythonAnywhere
2. Create a new directory: `btst-strategy`
3. Upload all files from your local `btst-strategy` folder:
   - `bot.py`
   - `config.py`
   - `strategy_btst.py`
   - `smart_api_helper.py`
   - `delta_api_helper.py`
   - `notifier.py`
   - `token_loader.py`
   - `requirements.txt`
   - `.env` (with your credentials)

---

## Step 2: Set Up Python Environment

1. **Open a Bash console** (Consoles → Bash)

2. **Navigate to your project**:
   ```bash
   cd btst-strategy
   ```

3. **Create a virtual environment** (optional but recommended):
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   If you encounter issues, install packages individually:
   ```bash
   pip install SmartApi-python
   pip install pandas
   pip install pandas-ta
   pip install python-dotenv
   pip install logzero
   pip install requests
   pip install schedule
   pip install pyotp
   ```

---

## Step 3: Configure Environment Variables

### Option A: Using .env File (Easier)

1. **Create/Edit `.env` file** in the `btst-strategy` directory:
   ```bash
   nano .env
   ```

2. **Add your credentials**:
   ```env
   # Angel One API
   ANGEL_API_KEY=your_api_key_here
   ANGEL_CLIENT_ID=your_client_id_here
   ANGEL_PASSWORD=your_password_here
   ANGEL_TOTP_KEY=your_totp_key_here

   # Telegram - Crypto
   TELEGRAM_BOT_TOKEN_CRYPTO=your_crypto_bot_token
   TELEGRAM_CHAT_ID_CRYPTO=your_crypto_chat_id

   # Telegram - Equity
   TELEGRAM_BOT_TOKEN_EQUITY=your_equity_bot_token
   TELEGRAM_CHAT_ID_EQUITY=your_equity_chat_id

   # Delta Exchange (Optional)
   DELTA_API_KEY=your_delta_key
   DELTA_API_SECRET=your_delta_secret
   ```

3. **Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### Option B: Using PythonAnywhere Environment Variables

1. Go to **Files** → **Edit** → `.bashrc`
2. Add export statements:
   ```bash
   export ANGEL_API_KEY="your_api_key"
   export ANGEL_CLIENT_ID="your_client_id"
   # ... add all other variables
   ```
3. Reload: `source ~/.bashrc`

---

## Step 4: Test the Bot

Before setting up as an always-on task, test that everything works:

1. **Run the bot manually**:
   ```bash
   cd ~/btst-strategy
   source venv/bin/activate  # if using venv
   python bot.py
   ```

2. **Check for errors**:
   - Verify API connections (Angel One, Delta Exchange)
   - Check Telegram connectivity
   - Monitor logs for any issues

3. **Stop the test** (Ctrl+C) once you confirm it's working

---

## Step 5: Create Always-On Task

> **Note**: Always-On tasks require a **paid PythonAnywhere account** (Hacker plan or above)

1. **Go to Tasks tab** in PythonAnywhere dashboard

2. **Create a new Always-On task**:
   - **Description**: `BTST Strategy Bot`
   - **Command**: 
     ```bash
     /home/YOUR_USERNAME/btst-strategy/venv/bin/python /home/YOUR_USERNAME/btst-strategy/bot.py
     ```
     
     Replace `YOUR_USERNAME` with your PythonAnywhere username.
     
     If not using venv:
     ```bash
     python3.10 /home/YOUR_USERNAME/btst-strategy/bot.py
     ```

3. **Working directory**: `/home/YOUR_USERNAME/btst-strategy`

4. **Click "Create"**

5. **Start the task** by clicking the "Enable" button

---

## Step 6: Monitor the Bot

### View Logs

1. **Go to Tasks tab**
2. **Click on your task** to see logs
3. **Check for**:
   - Successful startup message
   - API connection confirmations
   - Scan cycle logs
   - Any error messages

### Alternative: Create a Log File

Modify the Always-On task command to redirect output to a log file:

```bash
/home/YOUR_USERNAME/btst-strategy/venv/bin/python /home/YOUR_USERNAME/btst-strategy/bot.py >> /home/YOUR_USERNAME/btst-strategy/bot.log 2>&1
```

Then view logs:
```bash
tail -f ~/btst-strategy/bot.log
```

---

## Step 7: Verify Telegram Alerts

1. **Wait for the next scan cycle** (15 minutes by default)
2. **Check your Telegram channels** for alerts
3. **If no alerts**:
   - Check logs for errors
   - Verify Telegram credentials in `.env`
   - Ensure bot has permission to send messages to channels

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Install missing packages
```bash
cd ~/btst-strategy
source venv/bin/activate
pip install <missing_package>
```

### Issue: "Angel One login failed"
**Solution**: 
- Verify TOTP key is correct
- Check API key permissions
- Ensure credentials in `.env` are correct

### Issue: "No data fetched"
**Solution**:
- Check internet connectivity
- Verify API credentials
- Check if market is open (for equity)

### Issue: Task keeps stopping
**Solution**:
- Check logs for errors
- Ensure all dependencies are installed
- Verify `.env` file is in the correct location

### Issue: "Permission denied" errors
**Solution**:
```bash
chmod +x ~/btst-strategy/bot.py
```

---

## Alternative: Using Scheduled Tasks (Free Tier)

If you're on the free tier and can't use Always-On tasks:

1. **Go to Tasks tab**
2. **Create a Scheduled task**:
   - **Time**: Choose hourly or specific times (e.g., 10:00, 11:00, 12:00, etc.)
   - **Command**: 
     ```bash
     cd /home/YOUR_USERNAME/btst-strategy && /home/YOUR_USERNAME/btst-strategy/venv/bin/python bot.py
     ```

3. **Note**: This will run the bot at specific times, not continuously. You'll need to modify `bot.py` to run once instead of in a loop.

### Modify bot.py for Scheduled Tasks

Replace the main function:

```python
def main():
    """Main entry point for scheduled execution"""
    logger.info("🚀 BTST Strategy Bot - Scheduled Run")
    
    # Run scan once
    run_scan()
    
    logger.info("✅ Scan completed. Exiting.")

if __name__ == "__main__":
    main()
```

---

## Updating the Bot

When you need to update the bot code:

### Using Git:
```bash
cd ~/btst-strategy
git pull origin main
```

### Manual:
1. Upload updated files via Files tab
2. Restart the Always-On task

### Restart Always-On Task:
1. Go to **Tasks** tab
2. Click **Disable** on your task
3. Wait a few seconds
4. Click **Enable** again

---

## Best Practices

1. **Monitor regularly**: Check logs daily for the first week
2. **Test alerts**: Ensure Telegram notifications are working
3. **Backup credentials**: Keep a secure copy of your `.env` file
4. **Update dependencies**: Periodically update packages
   ```bash
   pip install --upgrade -r requirements.txt
   ```
5. **Set up error notifications**: Consider adding error alerts to Telegram

---

## Cost Considerations

- **Free tier**: Can use scheduled tasks (limited frequency)
- **Hacker plan ($5/month)**: Supports Always-On tasks
- **Recommended**: Hacker plan for continuous monitoring

---

## Summary

Your BTST bot should now be running 24/7 on PythonAnywhere, scanning crypto and equity markets across all timeframes and sending alerts to your Telegram channels!

**Quick Checklist**:
- ✅ Code uploaded to PythonAnywhere
- ✅ Dependencies installed
- ✅ `.env` file configured with credentials
- ✅ Bot tested manually
- ✅ Always-On task created and enabled
- ✅ Logs monitored
- ✅ Telegram alerts verified

For issues or questions, check the logs first and refer to the troubleshooting section above.
