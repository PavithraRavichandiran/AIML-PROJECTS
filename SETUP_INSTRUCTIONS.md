# 🚀 Cricbuzz LiveStats - Setup Instructions

## Quick Start Guide (5 Minutes)

### Step 1: Environment Setup

```bash
# Navigate to project directory
cd Cricbuzz_LiveStats

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Initialization

```bash
# Initialize SQLite database with schema
python db/init_sqlite.py
```

Expected output:
```
✅ SQLite DB initialized at db/cricbuzz.db
```

### Step 3: API Configuration

1. **Get RapidAPI Key**:
   - Visit https://rapidapi.com/
   - Sign up for free account
   - Subscribe to "Cricbuzz Cricket" API
   - Copy your API key

2. **Configure API Keys**:
   - Open `config/api_keys.py`
   - Replace placeholder with your key:
   ```python
   RAPID_API_KEY = "your_actual_key_here"
   RAPID_API_HOST = "cricbuzz-cricket.p.rapidapi.com"
   ```

### Step 4: Run Application

```bash
streamlit run main.py
```

Your browser will automatically open to `http://localhost:8501`

---

## 🎯 First-Time Usage

### Populate Database with Real Data

#### Option 1: Import Players (No API needed)
1. Go to **Player Stats** page
2. Click **"📥 Import Top Indian Players"**
3. ✅ 32 players added instantly!

#### Option 2: Sync Live Matches (API required)
1. Go to **Live Scores** page
2. Click **"📥 Sync All Matches"**
3. Wait for sync to complete
4. ✅ All matches and scorecards saved!

### Test SQL Queries
1. Navigate to **SQL Analytics**
2. Select **Q1 - Players by Country**
3. Click **▶️ Execute Query**
4. ✅ See all Indian players!

### Try CRUD Operations
1. Go to **CRUD Operations**
2. Click **➕ Create** tab
3. Fill player details
4. Click **Create Player**
5. ✅ Toast notification appears!

---

## 🔍 Verification Checklist

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list` shows streamlit, pandas, requests)
- [ ] Database file exists at `db/cricbuzz.db`
- [ ] API keys configured in `config/api_keys.py`
- [ ] Application runs without errors (`streamlit run main.py`)
- [ ] All 5 pages load successfully
- [ ] Database shows 36+ players (after import)
- [ ] SQL queries execute successfully
- [ ] CRUD operations work with toast notifications

---

## ⚠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'streamlit'`
**Solution**: Activate virtual environment and install dependencies
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: `Failed to fetch live match data`
**Solution**: Check API key configuration and quota
- Verify API key in `config/api_keys.py`
- Check quota at https://rapidapi.com/developer/apps
- Use sample data if quota exhausted

### Issue: `Database not found`
**Solution**: Initialize database
```bash
python db/init_sqlite.py
```

### Issue: `ImportError: cannot import name 'X'`
**Solution**: Check file structure matches expected layout
- Ensure all `__init__.py` files exist in folders
- Verify file names match imports

---

## 📦 Dependencies Explained

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.31.0 | Web application framework |
| pandas | >=2.0.0 | Data manipulation and analysis |
| requests | >=2.31.0 | HTTP requests for API calls |
| sqlite3 | built-in | Database operations |

---

## 🎓 Learning Path

### For Beginners:
1. Start with **Home** page to understand features
2. Explore **SQL Analytics** with simple queries (Q1-Q5)
3. Try **CRUD Operations** to add your favorite players
4. View **Player Stats** to see API integration

### For Advanced Users:
1. Examine code structure in `utils/` and `pages/`
2. Modify SQL queries in **SQL Analytics**
3. Extend database schema in `db/init_sqlite.py`
4. Add new API endpoints in `utils/api_client.py`

---

## 💡 Tips & Best Practices

1. **Keep API key secure**: Never share or commit `api_keys.py`
2. **Monitor API quota**: Check usage at RapidAPI dashboard
3. **Backup database**: Copy `db/cricbuzz.db` before testing
4. **Use Git**: Version control your changes
5. **Read docstrings**: Hover over functions to see documentation

---

## 📞 Need Help?

- Check **Home** page for feature documentation
- Review code comments and docstrings
- Search for errors in terminal output
- Verify all setup steps completed

---

**✅ Setup Complete!** You're ready to explore Cricbuzz LiveStats!
