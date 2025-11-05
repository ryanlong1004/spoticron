"""
Live stats module for getting real-time Spotify data.
"""

import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import spotipy
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    from .auth import SpotifyAuthenticator
except ImportError:
    from auth import SpotifyAuthenticator


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
    genres: Optional[List[str]] = None  # For artists
    artist_names: Optional[List[str]] = None  # For tracks
    artist_ids: Optional[List[str]] = None  # For tracks
    album_name: Optional[str] = None  # For tracks
    album_id: Optional[str] = None  # For tracks
    preview_url: Optional[str] = None  # For tracks
    followers: Optional[int] = None  # For artists
    images: Optional[List[Dict[str, Any]]] = None


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
            current_playback = self.spotify.current_playback()

            if not current_playback or not current_playback.get("item"):
                return None

            track_data = current_playback["item"]

            return CurrentTrack(
                track_name=track_data["name"],
                artist_names=[artist["name"] for artist in track_data["artists"]],
                album_name=track_data["album"]["name"],
                duration_ms=track_data["duration_ms"],
                progress_ms=current_playback.get("progress_ms", 0),
                is_playing=current_playback.get("is_playing", False),
                track_id=track_data["id"],
                artist_ids=[artist["id"] for artist in track_data["artists"]],
                album_id=track_data["album"]["id"],
                popularity=track_data.get("popularity", 0),
                explicit=track_data.get("explicit", False),
                external_urls=track_data.get("external_urls", {}),
                preview_url=track_data.get("preview_url"),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        except (KeyError, ValueError, AttributeError) as e:
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

            if results and "items" in results:
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

        except (KeyError, ValueError, AttributeError) as e:
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

            if results and "items" in results:
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

            if results and "items" in results:
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
                    artist_counts, key=lambda x: artist_counts[x]
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

    def monitor_enhanced(
        self,
        duration_minutes: int = 0,  # 0 = indefinite
        interval_seconds: int = 5,
        previous_tracks: int = 3,
        next_tracks: int = 3,
    ) -> None:
        """
        Enhanced monitoring with smart updates and queue display.

        Args:
            duration_minutes: How long to monitor (in minutes). 0 = indefinite.
            interval_seconds: How often to check (in seconds).
            previous_tracks: Number of previous tracks to show.
            next_tracks: Number of upcoming tracks to show.
        """
        console = Console()
        start_time = time.time()
        indefinite = duration_minutes == 0
        end_time = (
            start_time + (duration_minutes * 60) if not indefinite else float("inf")
        )

        # Track previous state to avoid unnecessary updates
        last_track_id = None
        last_progress = 0

        console.print("🎵 Enhanced Monitoring Mode Started", style="bold green")
        if indefinite:
            console.print(
                f"⏱️  Duration: Indefinite (Ctrl+C to stop) | Update interval: {interval_seconds}s"
            )
        else:
            console.print(
                f"⏱️  Duration: {duration_minutes} minutes | Update interval: {interval_seconds}s"
            )
        console.print("")

        try:
            while time.time() < end_time:
                current = self.get_current_track()

                # Check if we need to update the display
                current_track_id = current.track_id if current else None
                current_progress = current.progress_ms if current else 0

                # Only update display if track changed or significant progress change
                progress_change = (
                    abs(current_progress - last_progress) > 10000
                )  # 10 seconds
                track_changed = current_track_id != last_track_id

                if track_changed or progress_change or last_track_id is None:
                    # Clear screen and update display
                    console.clear()
                    self._display_enhanced_monitoring_vertical(
                        console, current, previous_tracks, next_tracks
                    )

                    last_track_id = current_track_id
                    last_progress = current_progress

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            console.print("\n🛑 Monitoring stopped by user", style="bold red")

        if not indefinite:
            console.print(
                f"\n✅ Monitoring completed after {duration_minutes} minutes",
                style="bold green",
            )
        else:
            console.print("\n✅ Monitoring session ended", style="bold green")

    def _display_enhanced_monitoring_vertical(
        self,
        console: Console,
        current: Optional[CurrentTrack],
        previous_tracks: int,
        next_tracks: int,
    ) -> None:
        """Display the enhanced monitoring layout in vertical single column format."""
        # Header with better spacing
        console.print("")
        header_line = "─" * 70
        console.print(f"╭{header_line}╮", style="bold blue")
        console.print(
            "│" + " " * 22 + "Enhanced Monitoring Mode" + " " * 22 + "│",
            style="bold blue",
        )
        console.print(f"╰{header_line}╯", style="bold blue")
        console.print("")

        # Get data for all sections
        recent_tracks = self._get_recent_tracks_for_monitoring(previous_tracks)
        upcoming_tracks = self._get_upcoming_tracks_for_monitoring(next_tracks)

        # Create and display panels vertically
        current_panel = self._create_current_track_panel_vertical(current)
        console.print(current_panel)
        console.print("")

        recent_panel = self._create_recent_tracks_panel_vertical(recent_tracks)
        console.print(recent_panel)
        console.print("")

        upcoming_panel = self._create_upcoming_tracks_panel_vertical(upcoming_tracks)
        console.print(upcoming_panel)

        # Footer with controls
        console.print("")
        console.print("💡 Press Ctrl+C to stop monitoring", style="dim italic")

    def _display_enhanced_monitoring(
        self,
        console: Console,
        current: Optional[CurrentTrack],
        previous_tracks: int,
        next_tracks: int,
    ) -> None:
        """Display the enhanced monitoring layout."""
        # Header with better spacing
        console.print("")
        header_line = "─" * 70
        console.print(f"╭{header_line}╮", style="bold blue")
        console.print(
            "│" + " " * 22 + "Enhanced Monitoring Mode" + " " * 22 + "│",
            style="bold blue",
        )
        console.print(f"╰{header_line}╯", style="bold blue")
        console.print("")

        # Three-column layout using Rich layout
        from rich.columns import Columns

        # Get data for all sections
        recent_tracks = self._get_recent_tracks_for_monitoring(previous_tracks)
        upcoming_tracks = self._get_upcoming_tracks_for_monitoring(next_tracks)

        # Create panels for each section
        recent_panel = self._create_recent_tracks_panel(recent_tracks)
        current_panel = self._create_current_track_panel(current)
        upcoming_panel = self._create_upcoming_tracks_panel(upcoming_tracks)

        # Display in columns with consistent spacing
        columns = Columns(
            [recent_panel, current_panel, upcoming_panel], equal=True, expand=True
        )
        console.print(columns)

        # Footer with controls
        console.print("")
        console.print("💡 Press Ctrl+C to stop monitoring", style="dim italic")

    def _get_recent_tracks_for_monitoring(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent tracks for monitoring display."""
        try:
            if not self.spotify:
                return []
            recent = self.spotify.current_user_recently_played(limit=limit)
            if not recent or "items" not in recent:
                return []
            return [
                {
                    "name": item["track"]["name"],
                    "artists": [artist["name"] for artist in item["track"]["artists"]],
                    "played_at": item["played_at"],
                }
                for item in recent["items"]
            ]
        except Exception as e:
            print(f"Error getting recent tracks: {e}")
            return []

    def _get_upcoming_tracks_for_monitoring(self, limit: int) -> List[Dict[str, Any]]:
        """Get upcoming tracks in queue for monitoring display."""
        try:
            if not self.spotify:
                return [
                    {"name": "Queue unavailable", "artists": ["Not authenticated"]}
                    for _ in range(limit)
                ]

            queue = self.spotify.queue()
            upcoming = []

            # Get tracks from queue
            if queue and "queue" in queue:
                for item in queue.get("queue", [])[:limit]:
                    if item and item.get("name"):
                        upcoming.append(
                            {
                                "name": item["name"],
                                "artists": [
                                    artist["name"] for artist in item.get("artists", [])
                                ],
                            }
                        )

            # If queue is empty or insufficient, show placeholder
            while len(upcoming) < limit:
                upcoming.append(
                    {
                        "name": "No upcoming tracks",
                        "artists": ["Queue is empty"],
                    }
                )

            return upcoming
        except Exception as e:
            print(f"Error getting queue: {e}")
            return [
                {"name": "Queue unavailable", "artists": ["Error fetching queue"]}
                for _ in range(limit)
            ]

    def _create_recent_tracks_panel(self, recent_tracks: List[Dict[str, Any]]) -> Panel:
        """Create panel for recent tracks."""
        if not recent_tracks:
            content = "\n[dim]No recent tracks available[/dim]\n"
        else:
            lines = [""]  # Start with empty line for consistent spacing
            for i, track in enumerate(recent_tracks, 1):
                artist_str = ", ".join(track["artists"])
                # Truncate long names for better display
                track_name = (
                    track["name"][:28] + "..."
                    if len(track["name"]) > 28
                    else track["name"]
                )
                artist_name = (
                    artist_str[:28] + "..." if len(artist_str) > 28 else artist_str
                )

                lines.append(f"{i}. [bold]{track_name}[/bold]")
                lines.append(f"   [dim]{artist_name}[/dim]")
                if i < len(recent_tracks):  # Add spacing between tracks except last
                    lines.append("")
            lines.append("")  # End with empty line for consistent spacing
            content = "\n".join(lines)

        return Panel(
            content,
            title="🕐 Recent Tracks",
            title_align="left",
            border_style="green",
            padding=(0, 1),
            height=12,  # Fixed height for uniformity
        )

    def _create_current_track_panel(self, current: Optional[CurrentTrack]) -> Panel:
        """Create panel for current track."""
        if not current:
            content = "\n\n[dim]No track currently playing[/dim]\n\n"
        else:
            artist_str = ", ".join(current.artist_names)
            status = "▶️ Playing" if current.is_playing else "⏸️ Paused"
            progress = self._format_progress_bar(
                current.progress_ms, current.duration_ms
            )
            popularity = self._format_popularity_stars(current.popularity)
            time_info = f"{format_duration(current.progress_ms)} / {format_duration(current.duration_ms)}"

            # Truncate long names for better display
            track_name = (
                current.track_name[:35] + "..."
                if len(current.track_name) > 35
                else current.track_name
            )
            artist_name = (
                artist_str[:35] + "..." if len(artist_str) > 35 else artist_str
            )
            album_name = (
                current.album_name[:35] + "..."
                if len(current.album_name) > 35
                else current.album_name
            )

            content = f"""
🎵 [bold green]{track_name}[/bold green]

👤 [dim]{artist_name}[/dim]

💿 [dim]{album_name}[/dim]

{status}

⏱️  {time_info}

{progress}

⭐ {popularity}
"""

        return Panel(
            content,
            title="🎵 Now Playing",
            title_align="left",
            border_style="bright_blue",
            padding=(0, 1),
            height=12,  # Fixed height for uniformity
        )

    def _create_upcoming_tracks_panel(
        self, upcoming_tracks: List[Dict[str, Any]]
    ) -> Panel:
        """Create panel for upcoming tracks."""
        if not upcoming_tracks:
            content = "\n[dim]No upcoming tracks in queue[/dim]\n"
        else:
            lines = [""]  # Start with empty line for consistent spacing
            for i, track in enumerate(upcoming_tracks, 1):
                artist_str = ", ".join(track["artists"])
                if track["name"] == "No upcoming tracks":
                    lines.append(f"[dim]{track['name']}[/dim]")
                else:
                    # Truncate long names for better display
                    track_name = (
                        track["name"][:28] + "..."
                        if len(track["name"]) > 28
                        else track["name"]
                    )
                    artist_name = (
                        artist_str[:28] + "..." if len(artist_str) > 28 else artist_str
                    )

                    lines.append(f"{i}. [bold]{track_name}[/bold]")
                    lines.append(f"   [dim]{artist_name}[/dim]")
                    if i < len(
                        upcoming_tracks
                    ):  # Add spacing between tracks except last
                        lines.append("")
            lines.append("")  # End with empty line for consistent spacing
            content = "\n".join(lines)

        return Panel(
            content,
            title="⏭️ Up Next",
            title_align="left",
            border_style="yellow",
            padding=(0, 1),
            height=12,  # Fixed height for uniformity
        )

    def _format_progress_bar(self, progress_ms: int, duration_ms: int) -> str:
        """Create a progress bar for the current track."""
        if duration_ms == 0:
            return "📊 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0.0%"

        percentage = (progress_ms / duration_ms) * 100
        bar_width = 35  # Slightly shorter for better fit
        filled_blocks = int((percentage / 100) * bar_width)
        bar = "█" * filled_blocks + "░" * (bar_width - filled_blocks)

        return f"📊 {bar} {percentage:.1f}%"

    def _format_popularity_stars(self, popularity: int) -> str:
        """Format popularity as star rating."""
        stars = int(popularity / 20)  # Convert 0-100 to 0-5 stars
        full_stars = "⭐" * stars
        empty_stars = "☆" * (5 - stars)
        return f"{full_stars}{empty_stars} ({popularity}/100)"

    def _create_current_track_panel_vertical(
        self, current: Optional[CurrentTrack]
    ) -> Panel:
        """Create vertical panel for current track with more space."""
        if not current:
            content = "\n[dim]No track currently playing[/dim]\n"
        else:
            artist_str = ", ".join(current.artist_names)
            status = "▶️ Playing" if current.is_playing else "⏸️ Paused"
            progress = self._format_progress_bar_wide(
                current.progress_ms, current.duration_ms
            )
            popularity = self._format_popularity_stars(current.popularity)
            time_info = f"{format_duration(current.progress_ms)} / {format_duration(current.duration_ms)}"

            # No truncation needed in vertical layout - more space
            content = f"""
🎵 [bold green]{current.track_name}[/bold green]

👤 [dim]{artist_str}[/dim]

💿 [dim]{current.album_name}[/dim]

{status}     ⏱️  {time_info}

{progress}

⭐ {popularity}
"""

        return Panel(
            content,
            title="🎵 Now Playing",
            title_align="left",
            border_style="bright_blue",
            padding=(1, 2),
        )

    def _create_recent_tracks_panel_vertical(
        self, recent_tracks: List[Dict[str, Any]]
    ) -> Panel:
        """Create vertical panel for recent tracks with more space."""
        if not recent_tracks:
            content = "\n[dim]No recent tracks available[/dim]\n"
        else:
            lines = [""]
            for i, track in enumerate(recent_tracks, 1):
                artist_str = ", ".join(track["artists"])
                lines.append(
                    f"{i}. [bold]{track['name']}[/bold] - [dim]{artist_str}[/dim]"
                )
            lines.append("")
            content = "\n".join(lines)

        return Panel(
            content,
            title="🕐 Recent Tracks",
            title_align="left",
            border_style="green",
            padding=(1, 2),
        )

    def _create_upcoming_tracks_panel_vertical(
        self, upcoming_tracks: List[Dict[str, Any]]
    ) -> Panel:
        """Create vertical panel for upcoming tracks with more space."""
        if not upcoming_tracks:
            content = "\n[dim]No upcoming tracks in queue[/dim]\n"
        else:
            lines = [""]
            for i, track in enumerate(upcoming_tracks, 1):
                artist_str = ", ".join(track["artists"])
                if track["name"] == "No upcoming tracks":
                    lines.append(f"[dim]{track['name']}[/dim]")
                else:
                    lines.append(
                        f"{i}. [bold]{track['name']}[/bold] - [dim]{artist_str}[/dim]"
                    )
            lines.append("")
            content = "\n".join(lines)

        return Panel(
            content,
            title="⏭️ Up Next",
            title_align="left",
            border_style="yellow",
            padding=(1, 2),
        )

    def _format_progress_bar_wide(self, progress_ms: int, duration_ms: int) -> str:
        """Create a wider progress bar for vertical layout."""
        if duration_ms == 0:
            return "📊 " + "░" * 60 + " 0.0%"

        percentage = (progress_ms / duration_ms) * 100
        bar_width = 60  # Wider bar for single column layout
        filled_blocks = int((percentage / 100) * bar_width)
        bar = "█" * filled_blocks + "░" * (bar_width - filled_blocks)

        return f"📊 {bar} {percentage:.1f}%"


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
    console = Console()

    # Calculate progress
    progress_pct = (
        (track.progress_ms / track.duration_ms) * 100 if track.duration_ms > 0 else 0
    )

    # Create a beautiful track info display with consistent spacing
    track_info = Table.grid(padding=(0, 1))
    track_info.add_column(style="cyan", width=4, justify="center")
    track_info.add_column(style="white")

    # Add track details with consistent icons and spacing
    track_info.add_row(
        "🎵", f"[bold bright_white]{track.track_name}[/bold bright_white]"
    )
    track_info.add_row("", "")  # Spacing
    track_info.add_row(
        "�", f"[bright_yellow]{', '.join(track.artist_names)}[/bright_yellow]"
    )
    track_info.add_row("", "")  # Spacing
    track_info.add_row("💿", f"[dim bright_white]{track.album_name}[/dim bright_white]")
    track_info.add_row("", "")  # Spacing

    # Status with consistent styling
    status_icon = "▶️" if track.is_playing else "⏸️"
    status_text = (
        "[bright_green]Playing[/bright_green]"
        if track.is_playing
        else "[bright_yellow]Paused[/bright_yellow]"
    )
    track_info.add_row(status_icon, status_text)
    track_info.add_row("", "")  # Spacing

    # Time display
    current_time = f"[bright_cyan]{format_duration(track.progress_ms)}[/bright_cyan]"
    total_time = f"[dim]{format_duration(track.duration_ms)}[/dim]"
    track_info.add_row("⏱️", f"{current_time} / {total_time}")
    track_info.add_row("", "")  # Spacing

    # Progress bar with better visual
    progress_blocks = int(progress_pct // 2)
    remaining_blocks = 50 - progress_blocks
    progress_bar = (
        f"[bright_green]{'█' * progress_blocks}[/bright_green]"
        + f"[dim]{'░' * remaining_blocks}[/dim]"
    )
    track_info.add_row(
        "📊", f"{progress_bar} [bright_cyan]{progress_pct:.1f}%[/bright_cyan]"
    )
    track_info.add_row("", "")  # Spacing

    # Popularity with stars
    full_stars = track.popularity // 20
    stars = "⭐" * full_stars + "☆" * (5 - full_stars)
    track_info.add_row("⭐", f"{stars} [dim]({track.popularity}/100)[/dim]")

    # Create main panel
    panel = Panel(
        track_info,
        title="[bold bright_cyan]♪ Now Playing ♪[/bold bright_cyan]",
        border_style="bright_green",
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
            artists = ", ".join(track.artist_names) if track.artist_names else "Unknown"
            print(f"{i}. {track.name} by {artists}")

        # Test top artists
        print("\n" + "=" * 50)
        print("🌟 TOP ARTISTS (Medium Term)")
        print("=" * 50)
        top_artists = collector.get_top_artists("medium_term", 5)
        for i, artist in enumerate(top_artists, 1):
            genres_str = ", ".join(artist.genres[:3]) if artist.genres else "N/A"
            print(f"{i}. {artist.name} (Genres: {genres_str})")

    except Exception as e:
        print(f"Error: {e}")
