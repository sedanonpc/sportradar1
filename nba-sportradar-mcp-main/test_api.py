import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not SPORTRADAR_API_KEY:
    raise ValueError("SPORTRADAR_API_KEY environment variable is required")

# SportRadar NBA API base URL
BASE_URL = "https://api.sportradar.com/nba/production/v8"

async def test_nba_api():
    """Test the NBA API directly."""
    async with httpx.AsyncClient(base_url=BASE_URL, params={"api_key": SPORTRADAR_API_KEY}, timeout=30.0) as client:
        try:
            # Test the daily schedule endpoint
            print("Testing NBA daily schedule endpoint...")
            response = await client.get("/en/games/2024/06/17/schedule.json")
            response.raise_for_status()
            data = response.json()
            print(f"Response: {data}")
            
            # Check if it's NBA or MLB data
            if "league" in data and "alias" in data["league"]:
                print(f"League alias: {data['league']['alias']}")
                if data["league"]["alias"] == "MLB":
                    print("ERROR: Received MLB data instead of NBA data!")
                elif data["league"]["alias"] == "NBA":
                    print("SUCCESS: Received NBA data as expected!")
                else:
                    print(f"Unknown league: {data['league']['alias']}")
            else:
                print("Could not determine league from response")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_nba_api()) 