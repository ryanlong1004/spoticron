"""
Live stats module for getting real-time Spotify data.
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import spotipy
from .auth import SpotifyAuthenticator


@dataclass
class CurrentTrack:
    """Data class for current playing track information."""

    track_name: str
    artist_names: List[str]
    album_name: str
    duration_ms: int
    progress_ms: int
    is_playing: bool
    track_id: str
    artist_ids: List[str]
    album_id: str
    popularity: int
    explicit: bool
    external_urls: Dict[str, str]
    preview_url: Optional[str]
    timestamp: str


@dataclass
class RecentTrack:
    """Data class for recently played track information."""

    track_name: str
    artist_names: List[str]
    album_name: str
    track_id: str
    artist_ids: List[str]
    album_id: str
    played_at: str
    duration_ms: int
    popularity: int
    explicit: bool
    external_urls: Dict[str, str]
    preview_url: Optional[str]


@dataclass
class TopItem:
    """Data class for top tracks/artists information."""

    name: str
    item_id: str
    item_type: str  # 'track' or 'artist'
    popularity: int
    external_urls: Dict[str, str]
    genres: List[str] = None  # For artists
    artist_names: List[str] = None  # For tracks
    artist_ids: List[str] = None  # For tracks
    album_name: str = None  # For tracks
    album_id: str = None  # For tracks
    preview_url: Optional[str] = None  # For tracks
    followers: int = None  # For artists
    images: List[Dict[str, Any]] = None


class LiveStatsCollector:
    """Collects live statistics from Spotify API."""

    def __init__(self, spotify_client: Optional[spotipy.Spotify] = None):
        """
        Initialize the live stats collector.

        Args:
            spotify_client: Authenticated Spotify client. If None, will authenticate.
        """
        if spotify_client is None:
            auth = SpotifyAuthenticator()
            spotify_client = auth.authenticate()

        self.spotify = spotify_client

    def get_current_track(self) -> Optional[CurrentTrack]:
        """
        Get currently playing track information.

        Returns:
            CurrentTrack object or None if nothing is playing.
        """
        try:
            current = self.spotify.current_playback()

            if not current or not current.get("item"):
                return None

            track = current["item"]

            return CurrentTrack(
                track_name=track["name"],
                artist_names=[artist["name"] for artist in track["artists"]],
                album_name=track["album"]["name"],
                duration_ms=track["duration_ms"],
                progress_ms=current.get("progress_ms", 0),
                is_playing=current.get("is_playing", False),
                track_id=track["id"],
                artist_ids=[artist["id"] for artist in track["artists"]],
                album_id=track["album"]["id"],
                popularity=track.get("popularity", 0),
                explicit=track.get("explicit", False),
                external_urls=track.get("external_urls", {}),
                preview_url=track.get("preview_url"),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        except Exception as e:
            print(f"Error getting current track: {e}")
            return None

    def get_recently_played(self, limit: int = 50) -> List[RecentTrack]:
        """
        Get recently played tracks.

        Args:
            limit: Number of tracks to retrieve (max 50).

        Returns:
            List of RecentTrack objects.
        """
        try:
            results = self.spotify.current_user_recently_played(limit=min(limit, 50))
            recent_tracks = []

            for item in results["items"]:
                track = item["track"]

                recent_track = RecentTrack(
                    track_name=track["name"],
                    artist_names=[artist["name"] for artist in track["artists"]],
                    album_name=track["album"]["name"],
                    track_id=track["id"],
                    artist_ids=[artist["id"] for artist in track["artists"]],
                    album_id=track["album"]["id"],
                    played_at=item["played_at"],
                    duration_ms=track["duration_ms"],
                    popularity=track.get("popularity", 0),
                    explicit=track.get("explicit", False),
                    external_urls=track.get("external_urls", {}),
                    preview_url=track.get("preview_url"),
                )
                recent_tracks.append(recent_track)

            return recent_tracks

        except Exception as e:
            print(f"Error getting recently played tracks: {e}")
            return []

    def get_top_tracks(
        self, time_range: str = "medium_term", limit: int = 20
    ) -> List[TopItem]:
        """
        Get user's top tracks.

        Args:
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
            limit: Number of tracks to retrieve (max 50).

        Returns:
            List of TopItem objects for tracks.
        """
        try:
            results = self.spotify.current_user_top_tracks(
                time_range=time_range, limit=min(limit, 50)
            )

            top_tracks = []

            for track in results["items"]:
                top_item = TopItem(
                    name=track["name"],
                    item_id=track["id"],
                    item_type="track",
                    popularity=track.get("popularity", 0),
                    external_urls=track.get("external_urls", {}),
                    artist_names=[artist["name"] for artist in track["artists"]],
                    artist_ids=[artist["id"] for artist in track["artists"]],
                    album_name=track["album"]["name"],
                    album_id=track["album"]["id"],
                    preview_url=track.get("preview_url"),
                    images=track["album"].get("images", []),
                )
                top_tracks.append(top_item)

            return top_tracks

        except Exception as e:
            print(f"Error getting top tracks: {e}")
            return []

    def get_top_artists(
        self, time_range: str = "medium_term", limit: int = 20
    ) -> List[TopItem]:
        """
        Get user's top artists.

        Args:
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
            limit: Number of artists to retrieve (max 50).

        Returns:
            List of TopItem objects for artists.
        """
        try:
            results = self.spotify.current_user_top_artists(
                time_range=time_range, limit=min(limit, 50)
            )

            top_artists = []

            for artist in results["items"]:
                top_item = TopItem(
                    name=artist["name"],
                    item_id=artist["id"],
                    item_type="artist",
                    popularity=artist.get("popularity", 0),
                    external_urls=artist.get("external_urls", {}),
                    genres=artist.get("genres", []),
                    followers=artist["followers"]["total"],
                    images=artist.get("images", []),
                )
                top_artists.append(top_item)

            return top_artists

        except Exception as e:
            print(f"Error getting top artists: {e}")
            return []

    def get_playback_state(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed playback state information.

        Returns:
            Playback state dictionary or None.
        """
        try:
            return self.spotify.current_playback()
        except Exception as e:
            print(f"Error getting playback state: {e}")
            return None

    def get_listening_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current listening session.

        Returns:
            Dictionary with session summary information.
        """
        current = self.get_current_track()
        recent = self.get_recently_played(10)

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_track": asdict(current) if current else None,
            "is_active": current is not None and current.is_playing,
            "recent_tracks_count": len(recent),
            "recent_artists": list(
                set(artist for track in recent for artist in track.artist_names)
            ),
            "recent_unique_tracks": len(set(track.track_id for track in recent)),
        }

        if recent:
            # Calculate session statistics
            total_duration = sum(track.duration_ms for track in recent)
            summary["recent_total_duration_minutes"] = total_duration / (1000 * 60)

            # Most played artist in recent tracks
            artist_counts = {}
            for track in recent:
                for artist in track.artist_names:
                    artist_counts[artist] = artist_counts.get(artist, 0) + 1

            if artist_counts:
                summary["most_recent_artist"] = max(
                    artist_counts, key=artist_counts.get
                )

        return summary

    def monitor_listening(
        self, duration_minutes: int = 10, interval_seconds: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Monitor listening activity for a specified duration.

        Args:
            duration_minutes: How long to monitor (in minutes).
            interval_seconds: How often to check (in seconds).

        Returns:
            List of monitoring snapshots.
        """
        snapshots = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        print(f"Monitoring listening activity for {duration_minutes} minutes...")

        while time.time() < end_time:
            current = self.get_current_track()

            snapshot = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "current_track": asdict(current) if current else None,
                "is_playing": current.is_playing if current else False,
            }

            snapshots.append(snapshot)

            if current:
                print(
                    f"Playing: {current.track_name} by {', '.join(current.artist_names)}"
                )
            else:
                print("No track currently playing")

            time.sleep(interval_seconds)

        return snapshots


def format_duration(duration_ms: int) -> str:
    """
    Format duration from milliseconds to readable format.

    Args:
        duration_ms: Duration in milliseconds.

    Returns:
        Formatted duration string (e.g., "3:45").
    """
    seconds = duration_ms // 1000
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


def print_current_track(track: CurrentTrack):
    """
    Print beautifully formatted current track information with Rich styling.

    Args:
        track: CurrentTrack object to display.
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    # Calculate progress
    progress_pct = (
        (track.progress_ms / track.duration_ms) * 100 if track.duration_ms > 0 else 0
    )

    # Create a beautiful track info display
    track_info = Table.grid(padding=1)
    track_info.add_column(style="cyan", justify="right")
    track_info.add_column(style="white")

    # Add track details with icons
    track_info.add_row("🎵", f"[bold green]{track.track_name}[/bold green]")
    track_info.add_row(
        "👨‍🎤", f"[bold yellow]{', '.join(track.artist_names)}[/bold yellow]"
    )
    track_info.add_row("💿", f"[dim]{track.album_name}[/dim]")

    # Status with animated indicator
    status_icon = "▶️" if track.is_playing else "⏸️"
    status_text = (
        "[green]Playing[/green]" if track.is_playing else "[yellow]Paused[/yellow]"
    )
    track_info.add_row(status_icon, status_text)

    # Progress bar
    progress_bar = (
        f"[blue]{'█' * int(progress_pct // 2)}[/blue]"
        + f"[dim]{'░' * (50 - int(progress_pct // 2))}[/dim]"
    )

    track_info.add_row(
        "⏱️",
        f"{format_duration(track.progress_ms)} / {format_duration(track.duration_ms)}",
    )
    track_info.add_row("", f"{progress_bar} [dim]{progress_pct:.1f}%[/dim]")

    # Popularity with stars
    stars = "⭐" * (track.popularity // 20) + "☆" * (5 - (track.popularity // 20))
    track_info.add_row("📊", f"{stars} [dim]({track.popularity}/100)[/dim]")

    # Create main panel
    panel = Panel(
        track_info,
        title="[bold cyan]♪ Now Playing ♪[/bold cyan]",
        border_style="green",
        padding=(1, 2),
        expand=False,
    )

    console.print(panel)

    # Add extra info if available
    extras = []
    if track.preview_url:
        extras.append(f"🔗 [link={track.preview_url}]Preview Available[/link]")
    if hasattr(track, "explicit") and track.explicit:
        extras.append("🚫 [red]Explicit[/red]")

    if extras:
        console.print(" ".join(extras), style="dim", justify="center")

    console.print()


if __name__ == "__main__":
    # Test live stats collection
    try:
        collector = LiveStatsCollector()

        # Test current track
        current = collector.get_current_track()
        if current:
            print_current_track(current)
        else:
            print("No track currently playing")

        # Test recent tracks
        print("\n" + "=" * 50)
        print("🕒 RECENTLY PLAYED (Last 5)")
        print("=" * 50)
        recent = collector.get_recently_played(5)
        for i, track in enumerate(recent, 1):
            print(f"{i}. {track.track_name} by {', '.join(track.artist_names)}")

        # Test top tracks
        print("\n" + "=" * 50)
        print("🏆 TOP TRACKS (Medium Term)")
        print("=" * 50)
        top_tracks = collector.get_top_tracks("medium_term", 5)
        for i, track in enumerate(top_tracks, 1):
            print(f"{i}. {track.name} by {', '.join(track.artist_names)}")

        # Test top artists
        print("\n" + "=" * 50)
        print("🌟 TOP ARTISTS (Medium Term)")
        print("=" * 50)
        top_artists = collector.get_top_artists("medium_term", 5)
        for i, artist in enumerate(top_artists, 1):
            print(
                f"{i}. {artist.name} (Genres: {', '.join(artist.genres[:3]) if artist.genres else 'N/A'})"
            )

    except Exception as e:
        print(f"Error: {e}")
