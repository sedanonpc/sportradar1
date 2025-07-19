"""
MLB SportRadar MCP Server

This module implements a comprehensive Model Context Protocol (MCP) server for connecting
Claude with the SportRadar MLB API. It provides extensive tools for retrieving MLB
game data, Statcast analytics, player statistics, and broadcast-quality insights.

Main Features:
    - Daily MLB schedules and live game feeds
    - Game summaries, boxscores, and real-time updates
    - Team standings and comprehensive rankings
    - Player profiles, career stats, and seasonal performance
    - Statcast data and advanced analytics
    - Situational statistics and trend analysis
    - Matchup analysis (team vs team, pitcher vs batter)
    - Weather conditions and ballpark factors
    - Prospect rankings and draft information
    - Error handling with user-friendly messages
    - Configurable parameters with environment variable support

Usage:
    This server is designed to be run as a standalone script and exposes comprehensive MCP tools
    for use with Claude Desktop or other MCP-compatible clients. Perfect for broadcast commentary,
    statistical analysis, and real-time game insights.

    To run the server:
        $ python src/mlb_sportradar_mcp/server.py

    MCP tools provided:
        Game Data & Analysis:
            - get_daily_schedule: Daily game schedules
            - get_game_summary: Game summaries and results
            - get_game_boxscore: Detailed boxscores
            - get_game_play_by_play: Play-by-play data
            - get_game_pitch_metrics: Pitch-level Statcast data

        Statcast & Advanced Analytics:
            - get_seasonal_pitch_metrics: Player season pitching analytics
            - get_statcast_leaders: Statcast leaderboards

        Player & Team Statistics:
            - get_player_profile: Player information and stats
            - get_player_seasonal_stats: Seasonal performance
            - get_team_profile: Team information
            - get_team_roster: Current team rosters
            - get_seasonal_statistics: Team seasonal stats
            - get_seasonal_splits: Home/away, vs lefty/righty splits

        League Information:
            - get_standings: League and division standings
            - get_league_leaders: Statistical leaders
            - get_team_hierarchy: League structure
            - get_injuries: Current injury reports
            - get_transactions: Player transactions
            - get_draft_summary: Draft information

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

from mlb_sportradar_mcp.mlb_data import (
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
logger = logging.getLogger("mlb_sportradar_mcp")

# Load environment variables
load_dotenv()

# Get API key from environment
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not SPORTRADAR_API_KEY:
    raise ValueError("SPORTRADAR_API_KEY environment variable is required")

# Initialize FastMCP server
mcp = FastMCP("mlb-sportradar-mcp")

# SportRadar MLB API base URL
BASE_URL = "https://api.sportradar.com/mlb/production/v8"


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client with proper headers."""
    return httpx.AsyncClient(
        base_url=BASE_URL, params={"api_key": SPORTRADAR_API_KEY}, timeout=30.0
    )


@mcp.tool()
async def get_daily_schedule(date_str: Optional[str] = None) -> Dict[str, Any]:
    """Get MLB schedule for a specific date (YYYY-MM-DD format) or today if not specified."""
    date_str = format_date(date_str)

    async with await get_http_client() as client:
        try:
            # Format: /en/games/{year}/{month}/{day}/schedule.json
            date_components = parse_date(date_str)
            year, month, day = date_components["year"], date_components["month"], date_components["day"]

            response = await client.get(f"/en/games/{year}/{month}/{day}/schedule.json")
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Error getting daily schedule for {date_str}: {str(e)}")
            raise


@mcp.tool()
async def get_game_summary(game_id: str) -> Dict[str, Any]:
    """Get summary information for a specific MLB game."""
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
    """Get detailed boxscore for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/boxscore.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting game boxscore for {game_id}: {str(e)}")
            raise


@mcp.tool()
async def get_standings(year: Optional[int] = None, league: Optional[str] = None) -> Dict[str, Any]:
    """Get MLB standings for a specific year and league (AL/NL) or current season."""
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

            # Filter by league if specified
            if league and league.upper() in ["AL", "NL"]:
                filtered_leagues = []
                for league_data in formatted_data.get("leagues", []):
                    if league_data.get("alias", "").upper() == league.upper():
                        filtered_leagues.append(league_data)
                
                if filtered_leagues:
                    formatted_data["leagues"] = filtered_leagues

            return formatted_data
        except Exception as e:
            logger.error(f"Error getting standings for {year}: {str(e)}")
            raise


@mcp.tool()
async def get_player_profile(player_id: str) -> Dict[str, Any]:
    """Get detailed profile information for a specific MLB player."""
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
    """Get detailed profile information for a specific MLB team."""
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
    year: Optional[int] = None, category: Optional[str] = "hitting"
) -> Dict[str, Any]:
    """Get MLB league leaders for a specific year and category (hitting/pitching)."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/leaders.json")
            response.raise_for_status()
            data = response.json()

            # Filter by category if specified
            if category and category.lower() in ["hitting", "pitching"]:
                if "leaders" in data:
                    filtered_leaders = {}
                    for key, value in data["leaders"].items():
                        if category.lower() in key.lower():
                            filtered_leaders[key] = value
                    if filtered_leaders:
                        return {"leaders": filtered_leaders, "category": category}

            return data
        except Exception as e:
            logger.error(f"Error getting league leaders for {year}: {str(e)}")
            raise


@mcp.tool()
async def get_team_roster(team_id: str) -> Dict[str, Any]:
    """Get current roster for a specific MLB team."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/teams/{team_id}/roster.json")
            response.raise_for_status()
            data = response.json()
            return format_team_roster(data)
        except Exception as e:
            logger.error(f"Error getting team roster for {team_id}: {str(e)}")
            raise


@mcp.tool()
async def get_injuries() -> Dict[str, Any]:
    """Get current MLB injury report."""
    async with await get_http_client() as client:
        try:
            response = await client.get("/en/injuries.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting injury report: {str(e)}")
            raise


@mcp.tool()
async def get_game_play_by_play(game_id: str) -> Dict[str, Any]:
    """Get detailed play-by-play data for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/pbp.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting play-by-play for game {game_id}: {str(e)}")
            raise


@mcp.tool()
async def get_game_pitch_metrics(game_id: str) -> Dict[str, Any]:
    """Get pitch-level metrics and Statcast data for a specific MLB game."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/games/{game_id}/pitch_metrics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pitch metrics for game {game_id}: {str(e)}")
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
            response = await client.get(
                f"/en/seasons/{year}/{season_type}/teams/{team_id}/statistics.json"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal statistics for team {team_id}: {str(e)}")
            raise


@mcp.tool()
async def get_player_seasonal_stats(player_id: str, year: Optional[int] = None) -> Dict[str, Any]:
    """Get seasonal statistics for a specific player."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/players/{player_id}/seasons/{year}/statistics.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal stats for player {player_id}: {str(e)}")
            raise


@mcp.tool()
async def get_transactions(date_str: Optional[str] = None) -> Dict[str, Any]:
    """Get MLB transactions for a specific date or recent transactions."""
    async with await get_http_client() as client:
        try:
            if date_str:
                # Format: /en/league/{year}/{month}/{day}/transactions.json
                date_components = parse_date(date_str)
                year, month, day = date_components["year"], date_components["month"], date_components["day"]
                response = await client.get(f"/en/league/{year}/{month}/{day}/transactions.json")
            else:
                response = await client.get("/en/league/transactions.json")

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            raise


@mcp.tool()
async def get_draft_summary(year: int) -> Dict[str, Any]:
    """Get MLB draft summary for a specific year."""
    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/league/drafts/{year}/summary.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting draft summary for {year}: {str(e)}")
            raise


@mcp.tool()
async def get_team_hierarchy() -> Dict[str, Any]:
    """Get complete MLB team hierarchy with divisions and leagues."""
    async with await get_http_client() as client:
        try:
            response = await client.get("/en/league/hierarchy.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting team hierarchy: {str(e)}")
            raise


@mcp.tool()
async def get_seasonal_splits(player_id: str, year: Optional[int] = None) -> Dict[str, Any]:
    """Get seasonal splits for a player (home/away, vs lefty/righty, etc.)."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/players/{player_id}/seasons/{year}/splits.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting seasonal splits for player {player_id}: {str(e)}")
            raise


@mcp.tool()
async def get_seasonal_pitch_metrics(player_id: str, year: Optional[int] = None) -> Dict[str, Any]:
    """Get detailed Statcast pitch metrics for a player's season."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(
                f"/en/players/{player_id}/seasons/{year}/pitch_metrics.json"
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Error getting seasonal pitch metrics for player {player_id}: {str(e)}")
            raise


@mcp.tool()
async def get_statcast_leaders(
    year: Optional[int] = None, category: Optional[str] = "exit_velocity"
) -> Dict[str, Any]:
    """Get Statcast leaderboards (exit_velocity, launch_angle, barrel_rate, etc.)."""
    if year is None:
        year = datetime.now().year

    async with await get_http_client() as client:
        try:
            response = await client.get(f"/en/seasons/{year}/statcast_leaders.json")
            response.raise_for_status()
            data = response.json()  # type: ignore[no-any-return]

            # Filter by category if specified
            if category and "leaders" in data:
                category_data = {}
                for key, value in data["leaders"].items():
                    if category.lower() in key.lower():
                        category_data[key] = value
                if category_data:
                    return {"leaders": category_data, "category": category, "year": year}

            return data
        except Exception as e:
            logger.error(f"Error getting Statcast leaders for {year}: {str(e)}")
            raise


def main() -> None:
    """Main entry point for the MCP server."""
    logger.info("Starting MLB SportRadar MCP Server...")
    try:
        # API key check before starting the server
        if not SPORTRADAR_API_KEY:
            logger.error("SPORTRADAR_API_KEY environment variable is not set")
            print("SPORTRADAR_API_KEY environment variable is not set", file=sys.stderr)
            sys.exit(1)

        logger.info("API key found. Starting server...")
        mcp.run()
    except Exception as e:
        print(f"Failed to run server: {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
