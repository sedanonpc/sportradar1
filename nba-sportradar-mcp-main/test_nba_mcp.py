"""
Test file for NBA SportRadar MCP tools in Cursor.

This file demonstrates how to use the NBA MCP tools in Cursor.
Run this file in Cursor and use the MCP tools to get NBA data.
"""

# To use the NBA MCP tools in Cursor, simply import the functions from the nba_sportradar_mcp.server module
# and call them directly. The MCP server will handle the requests.

# Example 1: Get the NBA schedule for today
# Use the mcp_nba-sportradar-mcp_get_daily_schedule tool in Cursor

# Example 2: Get the NBA standings
# Use the mcp_nba-sportradar-mcp_get_standings tool in Cursor with conference="East" or conference="West"

# Example 3: Get information about a specific NBA team
# Use the mcp_nba-sportradar-mcp_get_team_profile tool in Cursor with team_id="583ecfa8-fb46-11e1-82cb-f4ce4684ea4c" (Lakers)

# Example 4: Get the NBA team hierarchy
# Use the mcp_nba-sportradar-mcp_get_team_hierarchy tool in Cursor

# Example 5: Get information about NBA injuries
# Use the mcp_nba-sportradar-mcp_get_injuries tool in Cursor

print("NBA MCP tools test file loaded successfully.")
print("Use the MCP tools in Cursor to get NBA data.")
print("For example, try using the mcp_nba-sportradar-mcp_get_daily_schedule tool.") 