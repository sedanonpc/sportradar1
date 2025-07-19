"""
Verify that our NBA MCP server is returning NBA data.
"""

import os
import sys
import asyncio
import json
from datetime import date

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from nba_sportradar_mcp.server import get_daily_schedule, get_team_hierarchy

async def verify_nba_data():
    """Verify that our NBA MCP server is returning NBA data."""
    try:
        # Test the daily schedule endpoint
        print("Testing NBA daily schedule endpoint...")
        
        # Get today's date
        today = date.today().strftime("%Y-%m-%d")
        print(f"Getting schedule for {today}...")
        
        # Call the MCP function directly
        result = await get_daily_schedule(today)
        
        # Check if it's NBA data
        if "league" in result and "alias" in result["league"]:
            print(f"League alias: {result['league']['alias']}")
            if result["league"]["alias"] == "MLB":
                print("ERROR: Received MLB data instead of NBA data!")
            elif result["league"]["alias"] == "NBA":
                print("SUCCESS: Received NBA data as expected!")
            else:
                print(f"Unknown league: {result['league']['alias']}")
        else:
            print("Could not determine league from response")
        
        # Test the team hierarchy endpoint
        print("\nTesting NBA team hierarchy endpoint...")
        result = await get_team_hierarchy()
        
        # Check if it's NBA data
        if "league" in result and "alias" in result["league"]:
            print(f"League alias: {result['league']['alias']}")
            if result["league"]["alias"] == "MLB":
                print("ERROR: Received MLB data instead of NBA data!")
            elif result["league"]["alias"] == "NBA":
                print("SUCCESS: Received NBA data as expected!")
            else:
                print(f"Unknown league: {result['league']['alias']}")
        else:
            print("Could not determine league from response")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_nba_data()) 