"""
Authentication module for Spotify API integration.
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


class SpotifyAuthError(Exception):
    """Custom exception for Spotify authentication errors."""


class SpotifyTokenError(Exception):
    """Custom exception for Spotify token-related errors."""


# Load environment variables
load_dotenv()


class SpotifyAuthenticator:
    """Handles Spotify authentication using OAuth2 flow."""

    def __init__(self, cache_path: Optional[str] = None):
        """
        Initialize the Spotify authenticator.

        Args:
            cache_path: Path to store token cache. If None, uses default from env.
        """
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify credentials not found. Please set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET environment variables."
            )

        # Set up cache directory
        if cache_path is None:
            cache_path = os.getenv("TOKEN_CACHE_PATH", "data/cache/.spotify_token_cache")

        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Define required scopes for comprehensive access
        self.scope = [
            "user-read-currently-playing",
            "user-read-recently-played",
            "user-top-read",
            "user-read-playback-state",
            "user-library-read",
            "playlist-read-private",
            "playlist-read-collaborative",
        ]

        self.sp_oauth = None
        self.spotify = None

    def authenticate(self) -> spotipy.Spotify:
        """
        Authenticate with Spotify and return a Spotify client instance.

        Returns:
            Authenticated Spotify client instance.
        """
        # Initialize OAuth handler
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=" ".join(self.scope),
            cache_path=str(self.cache_path),
            show_dialog=True,
        )

        # Get token
        token_info = self._get_token()

        if not token_info:
            raise SpotifyAuthError("Failed to authenticate with Spotify")

        # Create Spotify client
        self.spotify = spotipy.Spotify(auth=token_info["access_token"])

        return self.spotify

    def _get_token(self) -> Optional[Dict[str, Any]]:
        """
        Get a valid token, refreshing if necessary.

        Returns:
            Token info dictionary or None if authentication fails.
        """
        if self.sp_oauth is None:
            raise SpotifyAuthError("OAuth handler not initialized")

        token_info = self.sp_oauth.get_cached_token()

        if not token_info:
            # No cached token, need to authenticate
            auth_url = self.sp_oauth.get_authorize_url()
            print(f"\nPlease visit this URL to authorize the application:\n{auth_url}\n")

            response = input("Enter the URL you were redirected to: ").strip()

            try:
                code = self.sp_oauth.parse_response_code(response)
                token_info = self.sp_oauth.get_access_token(code)
            except (ValueError, KeyError) as e:
                print(f"Error during authentication: {e}")
                return None

        # Check if token needs refresh
        if token_info and self._is_token_expired(token_info):
            print("Token expired, refreshing...")
            refresh_token = token_info.get("refresh_token")
            if refresh_token:
                token_info = self.sp_oauth.refresh_access_token(refresh_token)
            else:
                print("No refresh token available")
                return None

        return token_info

    def _is_token_expired(self, token_info: Dict[str, Any]) -> bool:
        """
        Check if the token is expired.

        Args:
            token_info: Token information dictionary.

        Returns:
            True if token is expired, False otherwise.
        """
        now = int(time.time())
        return token_info["expires_at"] - now < 60  # Refresh if expires within 1 minute

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information.

        Returns:
            User information dictionary or None if failed.
        """
        if not self.spotify:
            raise SpotifyAuthError("Not authenticated. Call authenticate() first.")

        try:
            return self.spotify.current_user()
        except (AttributeError, ValueError) as e:
            print(f"Error getting user info: {e}")
            return None

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.

        Returns:
            True if authenticated, False otherwise.
        """
        return self.spotify is not None

    def revoke_token(self):
        """Revoke the current token and clear cache."""
        if self.cache_path.exists():
            self.cache_path.unlink()
        self.spotify = None
        self.sp_oauth = None
        print("Token revoked and cache cleared.")


def get_authenticated_spotify() -> spotipy.Spotify:
    """
    Convenience function to get an authenticated Spotify client.

    Returns:
        Authenticated Spotify client instance.
    """
    authenticator = SpotifyAuthenticator()
    return authenticator.authenticate()


if __name__ == "__main__":
    # Test authentication
    try:
        auth = SpotifyAuthenticator()
        spotify = auth.authenticate()
        user_info = auth.get_user_info()

        if user_info:
            print(f"Successfully authenticated as: {user_info['display_name']} ({user_info['id']})")
        else:
            print("Authentication successful but couldn't get user info.")

    except (SpotifyAuthError, SpotifyTokenError, ValueError) as e:
        print(f"Authentication failed: {e}")
