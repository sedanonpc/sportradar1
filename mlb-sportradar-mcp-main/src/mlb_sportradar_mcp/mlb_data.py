"""
MLB data processing functions for the SportRadar MCP server.

This module contains helper functions for processing and formatting
MLB data from the SportRadar API.
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mlb_sportradar_mcp.mlb_data")


def format_date(date_str: Optional[str] = None) -> str:
    """Format date string to YYYY-MM-DD or return today's date if None."""
    if date_str is None:
        return date.today().strftime("%Y-%m-%d")
    return date_str


def parse_date(date_str: str) -> Dict[str, str]:
    """Parse a date string into year, month, day components."""
    date_parts = date_str.split("-")
    if len(date_parts) != 3:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    return {
        "year": date_parts[0],
        "month": date_parts[1],
        "day": date_parts[2]
    }


def format_game_summary(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format game summary data for better readability."""
    if not game_data:
        return {}
    
    # Extract key information
    summary = {
        "game_id": game_data.get("id", ""),
        "status": game_data.get("status", ""),
        "scheduled": game_data.get("scheduled", ""),
        "home_team": {},
        "away_team": {},
        "venue": game_data.get("venue", {}),
        "broadcast": game_data.get("broadcast", {}),
    }
    
    # Extract team information
    if "home" in game_data:
        summary["home_team"] = {
            "id": game_data["home"].get("id", ""),
            "name": game_data["home"].get("name", ""),
            "market": game_data["home"].get("market", ""),
            "abbr": game_data["home"].get("abbr", ""),
            "runs": game_data["home"].get("runs", 0),
            "hits": game_data["home"].get("hits", 0),
            "errors": game_data["home"].get("errors", 0),
        }
    
    if "away" in game_data:
        summary["away_team"] = {
            "id": game_data["away"].get("id", ""),
            "name": game_data["away"].get("name", ""),
            "market": game_data["away"].get("market", ""),
            "abbr": game_data["away"].get("abbr", ""),
            "runs": game_data["away"].get("runs", 0),
            "hits": game_data["away"].get("hits", 0),
            "errors": game_data["away"].get("errors", 0),
        }
    
    return summary


def format_standings(standings_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format standings data for better readability."""
    if not standings_data or "standings" not in standings_data:
        return standings_data
    
    formatted = {
        "season": standings_data.get("season", {}),
        "leagues": []
    }
    
    # Process leagues
    if "standings" in standings_data and "leagues" in standings_data["standings"]:
        for league in standings_data["standings"]["leagues"]:
            league_data = {
                "id": league.get("id", ""),
                "name": league.get("name", ""),
                "alias": league.get("alias", ""),
                "divisions": []
            }
            
            # Process divisions
            if "divisions" in league:
                for division in league["divisions"]:
                    division_data = {
                        "id": division.get("id", ""),
                        "name": division.get("name", ""),
                        "alias": division.get("alias", ""),
                        "teams": []
                    }
                    
                    # Process teams
                    if "teams" in division:
                        for team in division["teams"]:
                            team_data = {
                                "id": team.get("id", ""),
                                "name": team.get("name", ""),
                                "market": team.get("market", ""),
                                "abbr": team.get("abbr", ""),
                                "win": team.get("win", 0),
                                "loss": team.get("loss", 0),
                                "pct": team.get("win_p", 0),
                                "gb": team.get("games_back", 0),
                                "streak": team.get("streak", ""),
                                "home": f"{team.get('home_win', 0)}-{team.get('home_loss', 0)}",
                                "away": f"{team.get('away_win', 0)}-{team.get('away_loss', 0)}"
                            }
                            division_data["teams"].append(team_data)
                    
                    league_data["divisions"].append(division_data)
            
            formatted["leagues"].append(league_data)
    
    return formatted


def format_player_profile(player_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format player profile data for better readability."""
    if not player_data:
        return {}
    
    profile = {
        "id": player_data.get("id", ""),
        "first_name": player_data.get("first_name", ""),
        "last_name": player_data.get("last_name", ""),
        "full_name": f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}",
        "position": player_data.get("position", ""),
        "primary_position": player_data.get("primary_position", ""),
        "jersey_number": player_data.get("jersey_number", ""),
        "status": player_data.get("status", ""),
        "birth_date": player_data.get("birth_date", ""),
        "height": player_data.get("height", ""),
        "weight": player_data.get("weight", ""),
        "throw_hand": player_data.get("throw_hand", ""),
        "bat_hand": player_data.get("bat_hand", ""),
        "high_school": player_data.get("high_school", ""),
        "college": player_data.get("college", ""),
        "draft": player_data.get("draft", {}),
        "team": {}
    }
    
    # Extract team information
    if "team" in player_data:
        profile["team"] = {
            "id": player_data["team"].get("id", ""),
            "name": player_data["team"].get("name", ""),
            "market": player_data["team"].get("market", ""),
            "abbr": player_data["team"].get("abbr", "")
        }
    
    # Extract statistics if available
    if "seasons" in player_data:
        profile["seasons"] = player_data["seasons"]
    
    return profile


def format_team_roster(roster_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format team roster data for better readability."""
    if not roster_data:
        return {}
    
    formatted_roster = {
        "team": {
            "id": roster_data.get("id", ""),
            "name": roster_data.get("name", ""),
            "market": roster_data.get("market", ""),
            "abbr": roster_data.get("abbr", "")
        },
        "players": {
            "pitchers": [],
            "catchers": [],
            "infielders": [],
            "outfielders": [],
            "designated_hitters": [],
            "others": []
        }
    }
    
    # Process players by position
    if "players" in roster_data:
        for player in roster_data["players"]:
            player_info = {
                "id": player.get("id", ""),
                "first_name": player.get("first_name", ""),
                "last_name": player.get("last_name", ""),
                "full_name": f"{player.get('first_name', '')} {player.get('last_name', '')}",
                "jersey_number": player.get("jersey_number", ""),
                "position": player.get("position", ""),
                "primary_position": player.get("primary_position", ""),
                "status": player.get("status", "")
            }
            
            # Categorize by position
            position = player.get("primary_position", "").upper()
            if position in ["P", "SP", "RP", "CL"]:
                formatted_roster["players"]["pitchers"].append(player_info)
            elif position == "C":
                formatted_roster["players"]["catchers"].append(player_info)
            elif position in ["1B", "2B", "3B", "SS", "IF"]:
                formatted_roster["players"]["infielders"].append(player_info)
            elif position in ["LF", "CF", "RF", "OF"]:
                formatted_roster["players"]["outfielders"].append(player_info)
            elif position == "DH":
                formatted_roster["players"]["designated_hitters"].append(player_info)
            else:
                formatted_roster["players"]["others"].append(player_info)
    
    return formatted_roster 