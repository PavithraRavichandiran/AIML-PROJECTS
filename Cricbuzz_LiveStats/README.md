# 🏏 Cricbuzz LiveStats

**Real-time Cricket Analytics & Data Management Platform**

A comprehensive cricket analytics dashboard built with Streamlit, Python, and SQL. Features live match tracking, player statistics, SQL analytics engine, and complete CRUD operations.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Usage Guide](#usage-guide)
- [SQL Analytics](#sql-analytics)
- [API Integration](#api-integration)
- [Contributing](#contributing)

---

## ✨ Features

### 📡 Live Data Integration
- Real-time match updates from Cricbuzz API
- Auto-sync functionality for matches & scorecards
- Detailed player profiles with batting/bowling statistics
- Live scorecard with innings breakdown

### 📈 SQL Analytics Engine
- 25 pre-built analytical queries (Easy/Medium/Hard)
- Custom query execution capability
- Export results to CSV
- Query performance metrics

### 🛠️ Data Management (CRUD)
- **Create**: Add new players with auto-generated IDs
- **Read**: Search and filter players by name/country/role
- **Update**: Edit player information with validation
- **Delete**: Remove players with confirmation (safe delete)

### 🎨 Modern Interface
- Responsive Streamlit UI
- Toast notifications for user feedback
- Interactive data tables with sorting
- Real-time database statistics dashboard

---

## 🔧 Tech Stack

| Category | Technology |
|----------|-----------|
| **Frontend** | Streamlit, Python 3.11+ |
| **Backend** | Python, SQLite |
| **Database** | SQLite (MySQL/PostgreSQL compatible) |
| **API** | RapidAPI, Cricbuzz Cricket API |
| **Data Processing** | Pandas |
| **HTTP Client** | Requests |

---

## 📁 Project Structure

```
Cricbuzz_LiveStats/
├── main.py                       # Application entry point
├── requirements.txt              # Project dependencies
├── README.md                     # Project documentation
│
├── config/
│   └── api_keys.py              # RapidAPI credentials
│
├── pages/                        # Streamlit page modules
│   ├── __init__.py
│   ├── home.py                  # Home dashboard
│   ├── live_scores.py           # Live match tracking
│   ├── player_stats.py          # Player analytics
│   ├── sql_analytics.py         # 25 SQL queries
│   └── crud_operations.py       # Data management
│
├── utils/                        # Utility modules
│   ├── __init__.py
│   ├── api_client.py            # API integration functions
│   ├── db_sync.py               # Database sync utilities
│   ├── db_connection.py         # Database connector
│   └── crud_players.py          # Player CRUD logic
│
├── db/                           # Database files
│   ├── cricbuzz.db              # SQLite database
│   ├── init_sqlite.py           # Database initialization
│   └── sqlite_db.py             # Database utilities
│
└── data/                         # Data storage (optional)
```

---

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (for version control)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd Cricbuzz_LiveStats
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python db/init_sqlite.py
```

---

## ⚙️ Configuration

### 1. API Keys Setup

Create or edit `config/api_keys.py`:

```python
# RapidAPI Credentials
RAPID_API_KEY = "your_rapidapi_key_here"
RAPID_API_HOST = "cricbuzz-cricket.p.rapidapi.com"
```

**Get Your API Key:**
1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to [Cricbuzz Cricket API](https://rapidapi.com/cricketapilive/api/cricbuzz-cricket)
3. Copy your API key from the dashboard
4. Paste it in `config/api_keys.py`

### 2. Database Configuration

Default: SQLite (`db/cricbuzz.db`)

To use PostgreSQL or MySQL, update `utils/db_connection.py`:

```python
# PostgreSQL
DatabaseConnection.initialize('postgresql', {
    'host': 'localhost',
    'port': 5432,
    'database': 'cricbuzz',
    'user': 'your_user',
    'password': 'your_password'
})

# MySQL
DatabaseConnection.initialize('mysql', {
    'host': 'localhost',
    'port': 3306,
    'database': 'cricbuzz',
    'user': 'your_user',
    'password': 'your_password'
})
```

---

## 🗄️ Database Schema

### Tables

#### 1. **players**
```sql
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    role TEXT,
    batting_style TEXT,
    bowling_style TEXT
);
```

#### 2. **matches**
```sql
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    series_name TEXT,
    match_desc TEXT,
    match_format TEXT,
    team1 TEXT,
    team2 TEXT,
    venue_ground TEXT,
    venue_city TEXT,
    status TEXT,
    start_date INTEGER
);
```

#### 3. **scorecards**
```sql
CREATE TABLE scorecards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    innings_id INTEGER,
    bat_team TEXT,
    runs INTEGER,
    wickets INTEGER,
    overs REAL,
    runrate REAL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);
```

---

## 📖 Usage Guide

### Running the Application

```bash
streamlit run main.py
```

Access the dashboard at: `http://localhost:8501`

### Quick Start Workflow

#### 1️⃣ **Populate Database**
- Go to **Player Stats** → Click "📥 Import Top Indian Players"
- Go to **Live Scores** → Click "📥 Sync All Matches" (requires API quota)

#### 2️⃣ **Explore Analytics**
- Navigate to **SQL Analytics**
- Select from 25 pre-built queries
- Execute and download results

#### 3️⃣ **Manage Data**
- Visit **CRUD Operations**
- Create, Update, or Delete players
- View toast notifications for confirmations

---

## 📊 SQL Analytics

### 25 Analytical Queries

**Easy Level (Q1-Q10)**
- Player filtering by country
- Recent matches listing
- Top run scorers
- Match count by city/team
- Player role distribution

**Medium Level (Q11-Q18)**
- High-scoring innings analysis
- Average runs by team
- Economy rate analysis
- Match format distribution
- Batting/bowling styles breakdown

**Hard Level (Q19-Q25)**
- Highest individual scores
- Best run rates
- Close match analysis
- Team performance comparison
- Complete match overview with aggregations

### Custom Queries

Enable "🔍 View Query" checkbox to:
- View and edit SQL code
- Write custom queries
- Execute and export results

---

## 🔌 API Integration

### Endpoints Used

| Endpoint | Purpose | Rate Limit |
|----------|---------|------------|
| `/matches/v1/live` | Fetch live matches | 500/month (free) |
| `/mcenter/v1/{id}/hscard` | Match scorecard | 500/month (free) |
| `/stats/v1/player/search` | Search players | 500/month (free) |
| `/stats/v1/player/{id}` | Player profile | 500/month (free) |
| `/stats/v1/player/{id}/batting` | Batting stats | 500/month (free) |
| `/stats/v1/player/{id}/bowling` | Bowling stats | 500/month (free) |

### Error Handling

All API calls include:
- Connection timeout (10s)
- Retry logic for failed requests
- Graceful degradation (uses cached/sample data)
- User-friendly error messages

---

## 📝 Coding Standards

### PEP 8 Compliance
- 4 spaces for indentation
- Max line length: 100 characters
- Snake_case for functions/variables
- PascalCase for classes
- Docstrings for all functions

### Documentation
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    pass
```

---

## 🔒 Security Best Practices

1. **API Keys**: Never commit `api_keys.py` to version control
2. **Environment Variables**: Use `.env` for production
3. **SQL Injection**: Use parameterized queries
4. **Input Validation**: Sanitize all user inputs

### .gitignore
```
config/api_keys.py
*.db
venv/
__pycache__/
.env
```

---

## 🐛 Known Issues & Limitations

- ⚠️ Free API plan has monthly quota (500 requests)
- ⚠️ API may return 429 errors when quota exhausted
- ⚠️ Sample data included for demonstration
- ⚠️ Limited historical match data available

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is for educational purposes.

---

## 👥 Authors

- Pavithra Ravichandiran - Software Engineer

---

## 🙏 Acknowledgments

- [Cricbuzz](https://www.cricbuzz.com/) for cricket data
- [RapidAPI](https://rapidapi.com/) for API platform
- [Streamlit](https://streamlit.io/) for the amazing framework

---

## 📞 Support

For issues and questions:

- Contact: pavithraravichandiran192@gmail.com

---

**🏏 Cricbuzz LiveStats v2.0** | Built with ❤️ using Python & Streamlit
