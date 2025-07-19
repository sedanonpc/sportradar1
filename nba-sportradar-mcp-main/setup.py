from setuptools import find_packages, setup

setup(
    name="sportradar-mcp",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp[cli]>=1.3.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nba-sportradar-mcp=nba_sportradar_mcp.server:main",
        ],
    },
    python_requires=">=3.12",
)
