"""
Basic tests for Spoticron modules.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auth import SpotifyAuthenticator
from live_stats import LiveStatsCollector, CurrentTrack
from data_storage import SpotifyDataManager
from utils import format_duration, format_number, get_mood_from_features


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_format_duration(self):
        """Test duration formatting."""
        self.assertEqual(format_duration(245000), "4:05")
        self.assertEqual(format_duration(3661000), "1:01:01")
        self.assertEqual(format_duration(None), "0:00")
        self.assertEqual(format_duration(0), "0:00")

    def test_format_number(self):
        """Test number formatting."""
        self.assertEqual(format_number(1500), "1.5K")
        self.assertEqual(format_number(1500000), "1.5M")
        self.assertEqual(format_number(500), "500")
        self.assertEqual(format_number(None), "0")

    def test_get_mood_from_features(self):
        """Test mood detection from audio features."""
        # High energy, high valence
        features = {"energy": 0.8, "valence": 0.8, "danceability": 0.5}
        self.assertEqual(get_mood_from_features(features), "Energetic & Happy")

        # Low energy, low valence
        features = {"energy": 0.2, "valence": 0.2, "danceability": 0.5}
        self.assertEqual(get_mood_from_features(features), "Calm & Melancholic")

        # Empty features
        self.assertEqual(get_mood_from_features({}), "Unknown")


class TestCurrentTrack(unittest.TestCase):
    """Test CurrentTrack data class."""

    def test_current_track_creation(self):
        """Test creating a CurrentTrack instance."""
        track = CurrentTrack(
            track_name="Test Song",
            artist_names=["Test Artist"],
            album_name="Test Album",
            duration_ms=180000,
            progress_ms=90000,
            is_playing=True,
            track_id="test123",
            artist_ids=["artist123"],
            album_id="album123",
            popularity=75,
            explicit=False,
            external_urls={"spotify": "https://open.spotify.com/track/test123"},
            preview_url="https://preview.url",
            timestamp="2023-01-01T00:00:00Z",
        )

        self.assertEqual(track.track_name, "Test Song")
        self.assertEqual(track.artist_names, ["Test Artist"])
        self.assertTrue(track.is_playing)
        self.assertEqual(track.popularity, 75)


class TestSpotifyAuthenticator(unittest.TestCase):
    """Test Spotify authentication."""

    @patch("auth.SpotifyOAuth")
    @patch("auth.spotipy.Spotify")
    def test_authenticator_initialization(self, mock_spotify, mock_oauth):
        """Test authenticator initialization."""
        with patch.dict(
            os.environ,
            {"SPOTIFY_CLIENT_ID": "test_id", "SPOTIFY_CLIENT_SECRET": "test_secret"},
        ):
            auth = SpotifyAuthenticator()
            self.assertEqual(auth.client_id, "test_id")
            self.assertEqual(auth.client_secret, "test_secret")

    def test_authenticator_missing_credentials(self):
        """Test authenticator with missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                SpotifyAuthenticator()


class TestLiveStatsCollector(unittest.TestCase):
    """Test live stats collection."""

    @patch("live_stats.SpotifyAuthenticator")
    def test_collector_initialization(self, mock_auth):
        """Test collector initialization."""
        mock_spotify = Mock()
        collector = LiveStatsCollector(mock_spotify)
        self.assertEqual(collector.spotify, mock_spotify)

    @patch("live_stats.SpotifyAuthenticator")
    def test_get_current_track_no_playback(self, mock_auth):
        """Test getting current track when nothing is playing."""
        mock_spotify = Mock()
        mock_spotify.current_playback.return_value = None

        collector = LiveStatsCollector(mock_spotify)
        result = collector.get_current_track()

        self.assertIsNone(result)


class TestSpotifyDataManager(unittest.TestCase):
    """Test data storage manager."""

    @patch("data_storage.create_engine")
    @patch("data_storage.sessionmaker")
    def test_data_manager_initialization(self, mock_sessionmaker, mock_create_engine):
        """Test data manager initialization."""
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
            manager = SpotifyDataManager()
            self.assertIsNotNone(manager.config)
            mock_create_engine.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_modules_import(self):
        """Test that all modules can be imported."""
        try:
            import auth
            import live_stats
            import historical_stats
            import data_storage
            import utils
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")

    def test_data_flow(self):
        """Test basic data flow between modules."""
        # This would be a more comprehensive test in a real scenario
        # For now, just test that classes can be instantiated
        with patch.dict(
            os.environ,
            {"SPOTIFY_CLIENT_ID": "test_id", "SPOTIFY_CLIENT_SECRET": "test_secret"},
        ):
            try:
                # Test that we can create instances without errors
                mock_spotify = Mock()
                collector = LiveStatsCollector(mock_spotify)
                self.assertIsNotNone(collector)
            except Exception as e:
                self.fail(f"Data flow test failed: {e}")


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestUtils))
    test_suite.addTest(unittest.makeSuite(TestCurrentTrack))
    test_suite.addTest(unittest.makeSuite(TestSpotifyAuthenticator))
    test_suite.addTest(unittest.makeSuite(TestLiveStatsCollector))
    test_suite.addTest(unittest.makeSuite(TestSpotifyDataManager))
    test_suite.addTest(unittest.makeSuite(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
