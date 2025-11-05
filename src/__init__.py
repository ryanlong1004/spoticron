"""
Package initialization for Spoticron.
"""

__version__ = "1.0.0"
__author__ = "Spoticron Development Team"
__description__ = "Spotify Analytics Tool for comprehensive listening analysis"

from .auth import SpotifyAuthenticator, get_authenticated_spotify
from .data_storage import SpotifyDataManager, get_data_manager
from .historical_stats import HistoricalStatsAnalyzer
from .live_stats import CurrentTrack, LiveStatsCollector, RecentTrack, TopItem

__all__ = [
    "SpotifyAuthenticator",
    "get_authenticated_spotify",
    "LiveStatsCollector",
    "CurrentTrack",
    "RecentTrack",
    "TopItem",
    "HistoricalStatsAnalyzer",
    "SpotifyDataManager",
    "get_data_manager",
]
