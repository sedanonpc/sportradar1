# SportRadar MCP Server

Model Context Protocol (MCP) server for connecting Claude with the SportRadar API. It provides tools for accessing MLB and NBA game data, standings, player statistics, and more through the SportRadar API.

## Requirements

* Python 3.12 or higher
* Model Context Protocol (MCP) Python SDK
* httpx
* python-dotenv
* SportRadar API key(s)

## Setup

### 1. Get SportRadar API Key(s)

1. Sign up at [SportRadar Developer Portal](https://developer.sportradar.com/)
2. Get your MLB and/or NBA API key(s) (trial or production)

### 2. Install uv (recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Clone this repository

```bash
git clone https://github.com/yourusername/sportradar-mcp.git
cd sportradar-mcp
```

### 4. Create and activate a virtual environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
# Option 1: Using uv (recommended)
uv sync

# Option 2: Using pip with requirements.txt
pip install -r requirements.txt

# Option 3: Install as editable package
uv pip install -e .
```

### 6. Set up environment variables

Create a `.env` file in the project root with your SportRadar API key(s):

```bash
SPORTRADAR_API_KEY=your_api_key_here
```

## Usage

### 1. Configure Claude Desktop

First, install the MCP CLI globally:

```bash
uv tool install "mcp[cli]"
```

Then add these servers to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "MLB SportRadar": {
      "command": "/Users/<USERNAME>/.local/share/uv/tools/mcp/bin/mcp",
      "args": ["run", "/full/path/to/sportradar-mcp/src/mlb_sportradar_mcp/server.py"]
    },
    "NBA SportRadar": {
      "command": "/Users/<USERNAME>/.local/share/uv/tools/mcp/bin/mcp",
      "args": ["run", "/full/path/to/sportradar-mcp/src/nba_sportradar_mcp/server.py"]
    }
  }
}
```

**Important**: Replace `/full/path/to/` with the actual absolute path to your `sportradar-mcp` directory.

Restart Claude Desktop after saving the configuration.

### 2. Use the MCP servers with Claude

Once configured, Claude Desktop will have access to these tools:

#### MLB SportRadar Tools:

**Game Data:**
* **`get_daily_schedule`**: Get MLB schedule for a specific date or today
* **`get_game_summary`**: Get summary information for a specific game
* **`get_game_boxscore`**: Get detailed boxscore for a specific game
* **`get_game_play_by_play`**: Get detailed play-by-play data for a game
* **`get_game_pitch_metrics`**: Get pitch-level metrics and Statcast data

**Team & League:**
* **`get_standings`**: Get MLB standings for a specific year and league
* **`get_team_profile`**: Get detailed team information
* **`get_team_roster`**: Get current roster for a specific team
* **`get_team_hierarchy`**: Get complete MLB team hierarchy with divisions
* **`get_seasonal_statistics`**: Get seasonal statistics for a team

**Player Data:**
* **`get_player_profile`**: Get detailed player information
* **`get_player_seasonal_stats`**: Get seasonal statistics for a player
* **`get_seasonal_splits`**: Get player splits (home/away, vs lefty/righty, etc.)
* **`get_league_leaders`**: Get MLB league leaders in various categories

**League Information:**
* **`get_injuries`**: Get current MLB injury report
* **`get_transactions`**: Get MLB transactions for a specific date
* **`get_draft_summary`**: Get MLB draft summary for a specific year

#### NBA SportRadar Tools:

**Game Data:**
* **`get_daily_schedule`**: Get NBA schedule for a specific date or today
* **`get_game_summary`**: Get summary information for a specific game
* **`get_game_boxscore`**: Get detailed boxscore for a specific game
* **`get_game_play_by_play`**: Get detailed play-by-play data for a game

**Team & League:**
* **`get_standings`**: Get NBA standings for a specific year and conference
* **`get_team_profile`**: Get detailed team information
* **`get_team_roster`**: Get current roster for a specific team
* **`get_team_hierarchy`**: Get complete NBA team hierarchy with conferences and divisions
* **`get_seasonal_statistics`**: Get seasonal statistics for a team
* **`get_team_depth_chart`**: Get depth chart for a specific team

**Player Data:**
* **`get_player_profile`**: Get detailed player information
* **`get_player_seasonal_stats`**: Get seasonal statistics for a player
* **`get_league_leaders`**: Get NBA league leaders in various categories

**League Information:**
* **`get_injuries`**: Get current NBA injury report
* **`get_rankings`**: Get NBA team rankings for offense, defense, and other categories

**Example queries to try with Claude:**

MLB:
- "Show me today's MLB schedule"
- "Get the current AL standings"
- "What are the current batting leaders in MLB?"
- "Show me the injury report for MLB"
- "Get play-by-play data for game [game_id]"

NBA:
- "Show me today's NBA schedule"
- "Get the current Eastern Conference standings"
- "Who are the top scorers in the NBA this season?"
- "Show me the roster for the Lakers"
- "Get the depth chart for the Celtics"

## Development and testing

Install development dependencies and run the test suite with:

```bash
uv sync --all-extras
pytest -v tests
```

### Running the servers locally

To start the servers manually (useful when developing or testing), run:

```bash
# For MLB
mlb-sportradar-mcp

# For NBA
nba-sportradar-mcp
```

Alternatively, you can run them directly with:

```bash
# For MLB
uv run python src/mlb_sportradar_mcp/server.py

# For NBA
uv run python src/nba_sportradar_mcp/server.py
```

### Installing MCP CLI globally

If you want to use `mcp run` commands, install the MCP CLI globally:

```bash
uv tool install "mcp[cli]"
```

Then you can run:

```bash
# For MLB
mcp run src/mlb_sportradar_mcp/server.py

# For NBA
mcp run src/nba_sportradar_mcp/server.py
```

## API Endpoints

### MLB SportRadar API v8 endpoints:

- **Schedule**: `/en/games/{year}/{month}/{day}/schedule.json`
- **Game Summary**: `/en/games/{game_id}/summary.json`
- **Game Boxscore**: `/en/games/{game_id}/boxscore.json`
- **Standings**: `/en/seasons/{year}/standings.json`
- **Player Profile**: `/en/players/{player_id}/profile.json`
- **Team Profile**: `/en/teams/{team_id}/profile.json`
- **League Leaders**: `/en/seasons/{year}/leaders.json`
- **Team Roster**: `/en/teams/{team_id}/roster.json`
- **Injuries**: `/en/injuries.json`

### NBA SportRadar API v8 endpoints:

- **Schedule**: `/en/games/{year}/{month}/{day}/schedule.json`
- **Game Summary**: `/en/games/{game_id}/summary.json`
- **Game Boxscore**: `/en/games/{game_id}/boxscore.json`
- **Play-by-Play**: `/en/games/{game_id}/pbp.json`
- **Standings**: `/en/seasons/{year}/standings.json`
- **Player Profile**: `/en/players/{player_id}/profile.json`
- **Team Profile**: `/en/teams/{team_id}/profile.json`
- **League Leaders**: `/en/seasons/{year}/leaders.json`
- **Team Depth Chart**: `/en/teams/{team_id}/depth_chart.json`
- **Injuries**: `/en/league/injuries.json`
- **Hierarchy**: `/en/league/hierarchy.json`
- **Rankings**: `/en/seasons/{year}/REG/rankings.json`

## Rate Limits

Please be aware of SportRadar's API rate limits. The trial API typically has lower limits than production keys. Monitor your usage to avoid hitting rate limits.

## License

MIT
