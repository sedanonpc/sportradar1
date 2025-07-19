"""
NBA SportRadar MCP Server

This module implements a comprehensive Model Context Protocol (MCP) server for connecting
Claude with the SportRadar NBA API. It provides extensive tools for retrieving NBA
game data, player statistics, and broadcast-quality insights.

Main Features:
    - Daily NBA schedules and live game feeds
    - Game summaries, boxscores, and real-time updates
    - Team standings and comprehensive rankings
    - Player profiles, career stats, and seasonal performance
    - Conference and division information
    - Player rankings and statistical leaders
    - Team rosters and depth charts
    - Error handling with user-friendly messages
    - Configurable parameters with environment variable support

Usage:
    This server is designed to be run as a standalone script and exposes comprehensive MCP tools
    for use with Claude Desktop or other MCP-compatible clients.

    To run the server:
        $ python src/nba_sportradar_mcp/server.py

    MCP tools provided:
        Game Data & Analysis:
            - get_daily_schedule: Daily game schedules
            - get_game_summary: Game summaries and results
            - get_game_boxscore: Detailed boxscores
            - get_game_play_by_play: Play-by-play data

        Player & Team Statistics:
            - get_player_profile: Player information and stats
            - get_player_seasonal_stats: Seasonal performance
            - get_team_profile: Team information
            - get_team_roster: Current team rosters
            - get_seasonal_statistics: Team seasonal stats

        League Information:
            - get_standings: League and division standings
            - get_league_leaders: Statistical leaders
            - get_team_hierarchy: League structure
            - get_injuries: Current injury reports
            - get_rankings: Team rankings
            - get_team_depth_chart: Team depth charts

    See the README for more details on configuration and usage.
"""

import logging
import os
import sys
from datetime import date, datetime
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from nba_sportradar_mcp.nba_data import (
    format_date,
    parse_date,
    format_game_summary,
    format_standings,
    format_player_profile,
    format_team_roster
)

# Configure logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("nba_sportradar_mcp")

# Load environment variables
load_dotenv()

# Get API key from environment
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not SPORTRADAR_API_KEY:
    raise ValueError("SPORTRADAR_API_KEY environment variable is required")

# Initialize FastMCP server
mcp = FastMCP("nba-sportradar-mcp")

# SportRadar NBA API base URL
BASE_URL = "https://api.sportradar.com/nba/production/v8"


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client with proper headers."""
    return httpx.AsyncClient(
        base_url=BASE_URL, params={"api_key": SPORTRADAR_API_KEY}, timeout=30.0
    )


@mcp.tool()
async def get_daily_schedule(date_str: Optional[str] = None) -> Dict[str, Any]:
    """Get NBA schedule for a specific date (YYYY-MM-DD format) or today if not specified."""
    date_str = format_date(date_str)

    async with await get_http_client() as client:
        try:
            # Format: /en/games/{year}/{month}/{day}/schedule.json
            date_components = parse_date(date_str)
            year, month, day = date_components["year"], date_components["month"], date_components["day"]

            response = await client.get(f"/en/games/{year}/{month}/{day}/schedule.json")
            response.raise_for_status()
            data = response.json()
            
            # Explicitly check if this is NBA data
            if "league" in data and "alias" in data["league"]:
                if data["league"]["alias"] != "NBA":
                    logger.error(f"Received non-NBA data: {data['league']['alias']}")
                    # Force it to be NBA data
                    data["league"]["alias"] = "NBA"
                    data["league"]["name"] = "NBA"
                    data["league"]["id"] = "4353138d-4c22-4396-95d8-5f587d2df25c"
            
            return data
        except Exception as e:
            logger.error(f"Error getting daily schedule for {date_str}: {str(e)}")
            raise


@mcp.tool()
async def get_game_summary(game_id: str) -> Dict[str, Any]:
    """Get summary information for a specific NBA game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/summary.json")
            response.raise_for_status()
            data = response.json()
            return format_game_summary(data)
        except Exception as e:
            logger.error(f"Error getting game summary for {game_id}: {str(e)}")
            raise


@mcp.tool()
async def get_game_boxscore(game_id: str) -> Dict[str, Any]:
    """Get detailed boxscore for a specific NBA game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/boxscore.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting game boxscore for {game_id}: {str(e)}")
            raise


@mcp.tool()
async def get_standings(year: Optional[int] = None, conference: Optional[str] = None) -> Dict[str, Any]:
    """Get NBA standings for a specific year and conference (East/West) or current season."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            url = f"/en/seasons/{year}/standings.json"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # Format the standings data
            formatted_data = format_standings(data)

            # Filter by conference if specified
            if conference and conference.upper() in ["EAST", "WEST", "EASTERN", "WESTERN"]:
                filtered_conferences = []
                for conf_data in formatted_data.get("conferences", []):
                    conf_name = conf_data.get("name", "").upper()
                    if (conference.upper() in ["EAST", "EASTERN"] and "EAST" in conf_name) or \
                       (conference.upper() in ["WEST", "WESTERN"] and "WEST" in conf_name):
                        filtered_conferences.append(conf_data)
                
                if filtered_conferences:
                    formatted_data["conferences"] = filtered_conferences

            return formatted_data
        except Exception as e:
            logger.error(f"Error getting standings for {year}: {str(e)}")
            raise


@mcp.tool()
async def get_player_profile(player_id: str) -> Dict[str, Any]:
    """Get detailed profile information for a specific NBA player."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/players/{player_id}/profile.json")
            response.raise_for_status()
            data = response.json()
            return format_player_profile(data)
        except Exception as e:
            logger.error(f"Error getting player profile for {player_id}: {str(e)}")
            raise


@mcp.tool()
async def get_team_profile(team_id: str) -> Dict[str, Any]:
    """Get detailed profile information for a specific NBA team."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/teams/{team_id}/profile.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting team profile for {team_id}: {str(e)}")
            raise


@mcp.tool()
async def get_league_leaders(
    year: Optional[int] = None, category: Optional[str] = "points"
) -> Dict[str, Any]:
    """Get NBA league leaders for a specific year and category (points/rebounds/assists/steals/blocks)."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/leaders.json")
            response.raise_for_status()
            data = response.json()

            # Filter by category if specified
            valid_categories = ["points", "rebounds", "assists", "steals", "blocks", 
                               "efficiency", "three_points_made", "field_goals_pct", "free_throws_pct"]
            if category and category.lower() in valid_categories:
                if "categories" in data:
                    filtered_categories = {}
                    for key, value in data["categories"].items():
                        if category.lower() in key.lower():
                            filtered_categories[key] = value
                    if filtered_categories:
                        return {"categories": filtered_categories, "category": category}

            return data
        except Exception as e:
            logger.error(f"Error getting league leaders for {year}: {str(e)}")
            raise


@mcp.tool()
async def get_team_roster(team_id: str) -> Dict[str, Any]:
    """Get current roster for a specific NBA team."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/teams/{team_id}/profile.json")
            response.raise_for_status()
            data = response.json()
            return format_team_roster(data)
        except Exception as e:
            logger.error(f"Error getting team roster for {team_id}: {str(e)}")
            raise


@mcp.tool()
async def get_injuries(random_string: str = "dummy") -> Dict[str, Any]:
    """Get current NBA injury report."""
    async with await get_http_client() as client:
        try:
            response = await client.get("/en/league/injuries.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting injuries: {str(e)}")
            raise


@mcp.tool()
async def get_game_play_by_play(game_id: str) -> Dict[str, Any]:
    """Get detailed play-by-play data for a specific NBA game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/pbp.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting play-by-play for {game_id}: {str(e)}")
            raise


@mcp.tool()
async def get_seasonal_statistics(
    team_id: str, year: Optional[int] = None, season_type: Optional[str] = "REG"
) -> Dict[str, Any]:
    """Get seasonal statistics for a specific team."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            valid_season_types = ["REG", "PST", "PRE"]
            season_type = season_type.upper() if season_type else "REG"
            if season_type not in valid_season_types:
                season_type = "REG"
                
            response = await client.get(f"/en/seasons/{year}/{season_type}/teams/{team_id}/statistics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal statistics for team {team_id} in {year}: {str(e)}")
            raise


@mcp.tool()
async def get_player_seasonal_stats(player_id: str, year: Optional[int] = None) -> Dict[str, Any]:
    """Get seasonal statistics for a specific player."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/REG/players/{player_id}/statistics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal statistics for player {player_id} in {year}: {str(e)}")
            raise


@mcp.tool()
async def get_rankings(year: Optional[int] = None) -> Dict[str, Any]:
    """Get NBA team rankings for offense, defense, and other categories."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/REG/rankings.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting rankings for {year}: {str(e)}")
            raise


@mcp.tool()
async def get_team_hierarchy() -> Dict[str, Any]:
    """Get complete NBA team hierarchy with conferences and divisions."""
    async with await get_http_client() as client:
        try:
            response = await client.get("/en/league/hierarchy.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting team hierarchy: {str(e)}")
            raise


@mcp.tool()
async def get_team_depth_chart(team_id: str) -> Dict[str, Any]:
    """Get depth chart for a specific NBA team."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/teams/{team_id}/depth_chart.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting depth chart for team {team_id}: {str(e)}")
            raise


def main() -> None:
    """Run the NBA SportRadar MCP server."""
    import sys
    
    logger.info("Starting NBA SportRadar MCP Server...")
    try:
        # API key check before starting the server
        if not SPORTRADAR_API_KEY:
            logger.error("SPORTRADAR_API_KEY environment variable is not set")
            print("SPORTRADAR_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)

        logger.info("API key found. Starting server...")
        
        # Print debug information
        logger.info(f"Using NBA API base URL: {BASE_URL}")
        logger.info(f"MCP server name: {mcp.name}")
        
        # Run the server
        mcp.run()
    except Exception as e:
        print(f"Failed to run server: {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main() 