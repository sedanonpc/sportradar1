"""
NBA data processing functions for the SportRadar MCP server.

This module contains helper functions for processing and formatting
NBA data from the SportRadar API.
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nba_sportradar_mcp.nba_data")


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
    """Format NBA game summary data for better readability."""
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
            "alias": game_data["home"].get("alias", ""),
            "points": game_data["home"].get("points", 0),
        }
    
    if "away" in game_data:
        summary["away_team"] = {
            "id": game_data["away"].get("id", ""),
            "name": game_data["away"].get("name", ""),
            "market": game_data["away"].get("market", ""),
            "alias": game_data["away"].get("alias", ""),
            "points": game_data["away"].get("points", 0),
        }
    
    # Add quarter scores if available
    if "home" in game_data and "scoring" in game_data["home"]:
        summary["home_team"]["scoring"] = game_data["home"]["scoring"]
    
    if "away" in game_data and "scoring" in game_data["away"]:
        summary["away_team"]["scoring"] = game_data["away"]["scoring"]
    
    return summary


def format_standings(standings_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format NBA standings data for better readability."""
    if not standings_data or "standings" not in standings_data:
        return standings_data
    
    formatted = {
        "season": standings_data.get("season", {}),
        "conferences": []
    }
    
    # Process conferences
    if "standings" in standings_data and "conferences" in standings_data["standings"]:
        for conference in standings_data["standings"]["conferences"]:
            conference_data = {
                "id": conference.get("id", ""),
                "name": conference.get("name", ""),
                "alias": conference.get("alias", ""),
                "divisions": []
            }
            
            # Process divisions
            if "divisions" in conference:
                for division in conference["divisions"]:
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
                                "alias": team.get("alias", ""),
                                "wins": team.get("wins", 0),
                                "losses": team.get("losses", 0),
                                "win_pct": team.get("win_pct", 0),
                                "games_behind": team.get("games_behind", {}).get("division", 0),
                                "streak": team.get("streak", ""),
                                "home": f"{team.get('home_record', {}).get('wins', 0)}-{team.get('home_record', {}).get('losses', 0)}",
                                "away": f"{team.get('away_record', {}).get('wins', 0)}-{team.get('away_record', {}).get('losses', 0)}"
                            }
                            division_data["teams"].append(team_data)
                    
                    conference_data["divisions"].append(division_data)
            
            formatted["conferences"].append(conference_data)
    
    return formatted


def format_player_profile(player_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format NBA player profile data for better readability."""
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
        "college": player_data.get("college", ""),
        "high_school": player_data.get("high_school", ""),
        "draft": player_data.get("draft", {}),
        "team": {}
    }
    
    # Extract team information
    if "team" in player_data:
        profile["team"] = {
            "id": player_data["team"].get("id", ""),
            "name": player_data["team"].get("name", ""),
            "market": player_data["team"].get("market", ""),
            "alias": player_data["team"].get("alias", "")
        }
    
    # Extract statistics if available
    if "seasons" in player_data:
        profile["seasons"] = player_data["seasons"]
    
    return profile


def format_team_roster(roster_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format NBA team roster data for better readability."""
    if not roster_data:
        return {}
    
    formatted_roster = {
        "team": {
            "id": roster_data.get("id", ""),
            "name": roster_data.get("name", ""),
            "market": roster_data.get("market", ""),
            "alias": roster_data.get("alias", "")
        },
        "players": {
            "guards": [],
            "forwards": [],
            "centers": [],
            "two_way": [],
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
            if position in ["G", "PG", "SG", "G-F"]:
                formatted_roster["players"]["guards"].append(player_info)
            elif position in ["F", "SF", "PF", "F-G", "F-C"]:
                formatted_roster["players"]["forwards"].append(player_info)
            elif position in ["C", "C-F"]:
                formatted_roster["players"]["centers"].append(player_info)
            elif player.get("status", "") == "TEN-DAY" or player.get("status", "") == "TWO-WAY":
                formatted_roster["players"]["two_way"].append(player_info)
            else:
                formatted_roster["players"]["others"].append(player_info)
    
    return formatted_roster 