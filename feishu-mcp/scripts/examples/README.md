# Feishu Pro Examples

Real-world usage examples showing how to build powerful automation with Feishu Pro.

## Available Examples

### 1. Daily Standup Bot (`daily_standup.py`)

Automate daily standup reminders and summaries.

**Features:**
- Send standup reminders to team members
- Customizable meeting details and questions
- Batch send to multiple people
- Post-standup summary distribution

**Usage:**
```bash
# Send standup reminder
python daily_standup.py

# Send standup summary
python daily_standup.py summary "John: Working on feature X. Sarah: Bug fixes. Mike: Code review."
```

**Customization:**
Edit the `team` list and `message` template in the script to match your team structure.

**Scheduling:**
Use cron (Linux/Mac) or Task Scheduler (Windows) to run automatically:
```bash
# Linux/Mac crontab - runs every weekday at 9:50 AM
50 9 * * 1-5 /usr/bin/python3 /path/to/daily_standup.py

# Windows Task Scheduler
# Create task to run at 9:50 AM on weekdays
```

---

### 2. Auto Responder (`auto_responder.py`)

Automatically respond to unread messages with smart, context-aware replies.

**Features:**
- Detects message context (question, thanks, meeting request, etc.)
- Generates appropriate smart replies
- Marks messages as read after responding
- Vacation auto-reply mode

**Usage:**
```bash
# Auto-respond to unread messages
python auto_responder.py

# Vacation mode - send out-of-office replies
python auto_responder.py vacation
```

**Context Detection:**
The bot analyzes message content to choose the right reply:
- Questions ("?") → "Could you provide more details?"
- Thanks → "Got it, thanks!"
- Meeting requests → "Let's schedule a time to discuss this."
- Default → "Got it, thanks!"

**Vacation Setup:**
1. Edit the `vacation_message` in the script with your dates and backup contact
2. Run: `python auto_responder.py vacation`
3. The bot will send your vacation message to all chats with unread messages

**Scheduling:**
Run periodically to stay responsive:
```bash
# Every 30 minutes during work hours
*/30 9-17 * * 1-5 /usr/bin/python3 /path/to/auto_responder.py
```

---

### 3. Chat Backup & Analytics (`chat_backup.py`)

Backup chat histories and generate analytics reports.

**Features:**
- Backup all chats to JSON files
- Backup only important chats (with unreads)
- Generate word frequency analysis
- Message statistics (length, timing, etc.)
- Structured data export for further analysis

**Usage:**
```bash
# Backup all chats
python chat_backup.py all

# Backup only important chats (with unread messages)
python chat_backup.py important

# Analyze specific chat
python chat_backup.py analyze "Team Chat"
```

**Output:**
- `feishu_backup_YYYYMMDD_HHMMSS/` - Full backup directory
- `important_backup_YYYYMMDD/` - Important chats only
- `analysis_[chat]_YYYYMMDD.json` - Analytics report

**Analytics Report Includes:**
- Total message count
- Average message length
- Most common words (top 50)
- Time range (first to last message)
- Full message history

**Use Cases:**
- Compliance and record keeping
- Project documentation
- Data analysis and insights
- Before leaving a team/project
- Regular archival

**Scheduling:**
```bash
# Daily backup at midnight
0 0 * * * /usr/bin/python3 /path/to/chat_backup.py important

# Weekly full backup on Sundays at 2 AM
0 2 * * 0 /usr/bin/python3 /path/to/chat_backup.py all
```

---

## Creating Your Own Examples

All examples follow the same pattern:

```python
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Import Feishu Pro
sys.path.insert(0, str(Path(__file__).parent.parent))
from feishu_pro import FeishuPro

async def your_automation():
    # Initialize
    app = FeishuPro()
    await app.start()

    # Your automation logic here
    await app.send_message("chat", "message")

    # Clean up
    await app.close()

if __name__ == "__main__":
    asyncio.run(your_automation())
```

## Common Patterns

### Pattern 1: Scheduled Notification
```python
async def send_reminder():
    app = FeishuPro()
    await app.start()

    message = "Reminder: Submit your timesheet by EOD"
    recipients = ["Team1", "Team2", "Team3"]

    await app.batch_send(recipients, message)
    await app.close()
```

### Pattern 2: Monitor & Alert
```python
async def check_and_alert():
    app = FeishuPro()
    await app.start()

    # Check some condition
    if condition_is_met():
        await app.send_message("AlertsChat", "Alert: Condition detected!", enhance="formal")

    await app.close()
```

### Pattern 3: Interactive Bot
```python
async def process_commands():
    app = FeishuPro()
    await app.start()

    # Read messages
    messages = await app.read_messages("BotCommandsChat", limit=10)

    for msg in messages:
        text = msg["text"]

        if text.startswith("/status"):
            await app.send_message("BotCommandsChat", "Status: All systems operational")
        elif text.startswith("/help"):
            await app.send_message("BotCommandsChat", "Commands: /status, /help, /report")

    await app.close()
```

### Pattern 4: Data Aggregation
```python
async def aggregate_feedback():
    app = FeishuPro()
    await app.start()

    # Collect from multiple chats
    all_feedback = []
    chats = ["Feedback1", "Feedback2", "Feedback3"]

    for chat in chats:
        messages = await app.read_messages(chat, limit=50)
        all_feedback.extend(messages)

    # Process and send summary
    summary = f"Collected {len(all_feedback)} feedback messages"
    await app.send_message("Managers", summary, enhance="professional")

    await app.close()
```

## Advanced Integration

### With External APIs
```python
import requests

async def sync_with_api():
    app = FeishuPro()
    await app.start()

    # Fetch data from API
    response = requests.get("https://api.example.com/status")
    status = response.json()

    # Send to Feishu
    message = f"API Status: {status['state']}\nUptime: {status['uptime']}"
    await app.send_message("DevOps", message)

    await app.close()
```

### With Database
```python
import sqlite3

async def log_to_database():
    app = FeishuPro()
    await app.start()

    messages = await app.read_messages("Important", limit=100)

    # Store in database
    conn = sqlite3.connect("feishu_archive.db")
    cursor = conn.cursor()

    for msg in messages:
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?)",
                      (msg["timestamp"], msg["chat"], msg["text"]))

    conn.commit()
    conn.close()

    await app.close()
```

### With AI/ML
```python
async def sentiment_analysis():
    app = FeishuPro()
    await app.start()

    messages = await app.read_messages("CustomerFeedback", limit=100)

    # Analyze sentiment (pseudo-code)
    positive = sum(1 for msg in messages if analyze_sentiment(msg["text"]) > 0.5)
    negative = len(messages) - positive

    # Report
    report = f"Sentiment Analysis:\nPositive: {positive}\nNegative: {negative}"
    await app.send_message("Analytics", report)

    await app.close()
```

## Tips & Best Practices

### Error Handling
Always wrap operations in try-except:
```python
try:
    await app.send_message("chat", "message")
except Exception as e:
    print(f"[ERROR] Failed: {e}")
    # Maybe send alert to admin
    await app.send_message("Admin", f"Bot error: {e}")
```

### Rate Limiting
Add delays between batch operations:
```python
for chat in chats:
    await app.send_message(chat, message)
    await asyncio.sleep(2)  # 2 second delay
```

### Logging
Log all operations for debugging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Sending message to {chat}")
await app.send_message(chat, message)
logger.info("Message sent successfully")
```

### Configuration
Use config files instead of hardcoded values:
```python
import json

with open("config.json") as f:
    config = json.load(f)

team_members = config["team_members"]
schedule = config["schedule"]
```

## Deployment

### As a Service (Linux)
Create a systemd service:
```ini
[Unit]
Description=Feishu Auto Responder
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/scripts
ExecStart=/usr/bin/python3 auto_responder.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### With Docker
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements_pro.txt .
RUN pip install -r requirements_pro.txt
RUN playwright install chromium

COPY . .
CMD ["python", "your_example.py"]
```

### Cloud Functions
Adapt examples for serverless:
- AWS Lambda
- Google Cloud Functions
- Azure Functions

Note: You'll need to handle browser in headless mode and potentially use containerized browsers.

## Troubleshooting Examples

### Example Won't Start
```bash
# Ensure dependencies installed
pip install -r requirements_pro.txt
playwright install chromium

# Test Feishu Pro directly
python feishu_pro.py start
```

### Import Errors
```python
# Make sure parent directory is in path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Browser Issues
```bash
# Clear browser data
rm -rf ~/.feishu-browser-data/

# Reinstall playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

## Contributing Examples

Have a useful automation? Share it!

1. Create your example script
2. Add clear comments and docstrings
3. Test thoroughly
4. Submit a PR with:
   - The script file
   - Documentation in this README
   - Any additional config files needed

## License

All examples are provided under MIT License - free to use and modify.
