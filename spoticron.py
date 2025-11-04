#!/usr/bin/env python3
"""
Spoticron - Spotify Analytics CLI
Command-line interface for Spotify listening statistics and analysis.
"""

import click
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import print as rprint

# Import our modules
try:
    from src.auth import SpotifyAuthenticator
    from src.live_stats import LiveStatsCollector, print_current_track
    from src.historical_stats import HistoricalStatsAnalyzer, format_evolution_summary
    from src.data_storage import SpotifyDataManager
except ImportError:
    # Fallback for direct execution
    from auth import SpotifyAuthenticator
    from live_stats import LiveStatsCollector, print_current_track
    from historical_stats import HistoricalStatsAnalyzer, format_evolution_summary
    from data_storage import SpotifyDataManager

console = Console()


def show_banner():
    """Display the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                          SPOTICRON                           ║
║                   Spotify Analytics Tool                     ║
║                                                               ║
║          Get insights into your Spotify listening habits     ║
╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold green")


def handle_auth_error(func):
    """Decorator to handle authentication errors."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "authentication" in str(e).lower():
                console.print(
                    "❌ Authentication failed. Please check your credentials.",
                    style="bold red",
                )
                console.print(
                    "💡 Make sure you have set up your .env file with valid Spotify API credentials."
                )
                sys.exit(1)
            else:
                console.print(f"❌ Error: {e}", style="bold red")
                sys.exit(1)

    return wrapper


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Spoticron - Spotify Analytics Tool

    Get detailed insights into your Spotify listening habits with live stats,
    historical analysis, and personalized music discovery patterns.
    """
    show_banner()


@cli.command()
@click.option(
    "--show-details", "-d", is_flag=True, help="Show detailed track information"
)
def current(show_details):
    """Show currently playing track information."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Getting current track...", total=None)

        try:
            collector = LiveStatsCollector()
            current_track = collector.get_current_track()

            progress.remove_task(task)

            if current_track:
                if show_details:
                    print_current_track(current_track)
                else:
                    console.print(
                        Panel(
                            f"🎵 [bold]{current_track.track_name}[/bold]\n"
                            f"👨‍🎤 {', '.join(current_track.artist_names)}\n"
                            f"💿 {current_track.album_name}\n"
                            f"▶️ {'Playing' if current_track.is_playing else 'Paused'}",
                            title="Now Playing",
                            border_style="green",
                        )
                    )
            else:
                console.print("🔇 No track currently playing", style="yellow")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error getting current track: {e}", style="red")


@cli.command()
@click.option("--limit", "-l", default=10, help="Number of recent tracks to show")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed information")
def recent(limit, detailed):
    """Show recently played tracks."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Getting recent tracks...", total=None)

        try:
            collector = LiveStatsCollector()
            recent_tracks = collector.get_recently_played(limit)

            progress.remove_task(task)

            if recent_tracks:
                table = Table(title=f"🕒 Last {len(recent_tracks)} Played Tracks")
                table.add_column("#", style="cyan", width=3)
                table.add_column("Track", style="magenta")
                table.add_column("Artist(s)", style="green")
                if detailed:
                    table.add_column("Album", style="blue")
                    table.add_column("Played At", style="yellow")

                for i, track in enumerate(recent_tracks, 1):
                    played_time = datetime.fromisoformat(
                        track.played_at.replace("Z", "+00:00")
                    ).strftime("%H:%M")

                    row = [str(i), track.track_name, ", ".join(track.artist_names)]

                    if detailed:
                        row.extend([track.album_name, played_time])

                    table.add_row(*row)

                console.print(table)
            else:
                console.print("🔇 No recent tracks found", style="yellow")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error getting recent tracks: {e}", style="red")


@cli.command()
@click.option(
    "--time-range",
    "-t",
    type=click.Choice(["short_term", "medium_term", "long_term"]),
    default="medium_term",
    help="Time range for top tracks",
)
@click.option("--limit", "-l", default=10, help="Number of tracks to show")
def top_tracks(time_range, limit):
    """Show your top tracks for different time periods."""
    time_labels = {
        "short_term": "Last 4 Weeks",
        "medium_term": "Last 6 Months",
        "long_term": "All Time",
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Getting top tracks ({time_labels[time_range]})...", total=None
        )

        try:
            collector = LiveStatsCollector()
            top_tracks_data = collector.get_top_tracks(time_range, limit)

            progress.remove_task(task)

            if top_tracks_data:
                table = Table(
                    title=f"🏆 Top {len(top_tracks_data)} Tracks - {time_labels[time_range]}"
                )
                table.add_column("Rank", style="cyan", width=4)
                table.add_column("Track", style="magenta")
                table.add_column("Artist(s)", style="green")
                table.add_column("Popularity", style="yellow", width=10)

                for track in top_tracks_data:
                    table.add_row(
                        str(
                            track.name.split(".")[0]
                            if "." in str(track.name)
                            else len(table.rows) + 1
                        ),
                        track.name,
                        ", ".join(track.artist_names)
                        if track.artist_names
                        else "Unknown",
                        f"{track.popularity}/100",
                    )

                console.print(table)
            else:
                console.print("🔇 No top tracks found", style="yellow")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error getting top tracks: {e}", style="red")


@cli.command()
@click.option(
    "--time-range",
    "-t",
    type=click.Choice(["short_term", "medium_term", "long_term"]),
    default="medium_term",
    help="Time range for top artists",
)
@click.option("--limit", "-l", default=10, help="Number of artists to show")
def top_artists(time_range, limit):
    """Show your top artists for different time periods."""
    time_labels = {
        "short_term": "Last 4 Weeks",
        "medium_term": "Last 6 Months",
        "long_term": "All Time",
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Getting top artists ({time_labels[time_range]})...", total=None
        )

        try:
            collector = LiveStatsCollector()
            top_artists_data = collector.get_top_artists(time_range, limit)

            progress.remove_task(task)

            if top_artists_data:
                table = Table(
                    title=f"🌟 Top {len(top_artists_data)} Artists - {time_labels[time_range]}"
                )
                table.add_column("Rank", style="cyan", width=4)
                table.add_column("Artist", style="magenta")
                table.add_column("Genres", style="green")
                table.add_column("Popularity", style="yellow", width=10)
                table.add_column("Followers", style="blue", width=12)

                for i, artist in enumerate(top_artists_data, 1):
                    genres = ", ".join(artist.genres[:3]) if artist.genres else "N/A"
                    followers = f"{artist.followers:,}" if artist.followers else "N/A"

                    table.add_row(
                        str(i),
                        artist.name,
                        genres,
                        f"{artist.popularity}/100",
                        followers,
                    )

                console.print(table)
            else:
                console.print("🔇 No top artists found", style="yellow")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error getting top artists: {e}", style="red")


@cli.command()
@click.option("--export", "-e", is_flag=True, help="Export analysis to JSON file")
def analyze(export):
    """Perform comprehensive historical analysis of your listening habits."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Performing historical analysis...", total=None)

        try:
            analyzer = HistoricalStatsAnalyzer()

            # Get evolution analysis
            evolution = analyzer.analyze_listening_evolution()

            # Get diversity analysis
            diversity = analyzer.analyze_listening_diversity()

            # Get mood analysis
            mood = analyzer.get_mood_analysis()

            # Get discovery patterns
            discovery = analyzer.get_discovery_patterns()

            progress.remove_task(task)

            # Display evolution summary
            console.print(
                Panel(
                    format_evolution_summary(evolution),
                    title="Listening Evolution Analysis",
                    border_style="blue",
                )
            )

            # Display diversity metrics
            if diversity.get("time_ranges"):
                console.print("\n📊 [bold]Listening Diversity Metrics[/bold]")
                for time_range, metrics in diversity["time_ranges"].items():
                    time_label = {
                        "short_term": "Last Month",
                        "medium_term": "Last 6 Months",
                        "long_term": "All Time",
                    }.get(time_range, time_range)

                    console.print(f"\n[cyan]{time_label}:[/cyan]")
                    console.print(
                        f"  Unique Artists: {metrics.get('unique_artists', 0)}"
                    )
                    console.print(f"  Unique Genres: {metrics.get('unique_genres', 0)}")
                    console.print(
                        f"  Genre Diversity: {metrics.get('genre_entropy', 0):.2f}"
                    )

            # Display discovery patterns
            if discovery:
                discovery_rate = discovery.get("discovery_rate", 0)
                new_discoveries = len(discovery.get("new_discoveries", []))

                console.print(f"\n🔍 [bold]Discovery Patterns[/bold]")
                console.print(f"  Discovery Rate: {discovery_rate:.1f}%")
                console.print(f"  New Tracks Found: {new_discoveries}")

            # Export if requested
            if export:
                analysis_data = {
                    "evolution": evolution,
                    "diversity": diversity,
                    "mood": mood,
                    "discovery": discovery,
                    "timestamp": datetime.now().isoformat(),
                }

                output_file = (
                    f"data/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(analysis_data, f, indent=2, ensure_ascii=False)

                console.print(
                    f"\n💾 Analysis exported to: {output_file}", style="green"
                )

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error performing analysis: {e}", style="red")


@cli.command()
@click.option("--duration", "-d", default=5, help="Monitoring duration in minutes")
@click.option("--interval", "-i", default=30, help="Check interval in seconds")
def monitor(duration, interval):
    """Monitor your listening activity in real-time."""
    console.print(f"🎧 Monitoring listening activity for {duration} minutes...")
    console.print("Press Ctrl+C to stop monitoring\n")

    try:
        collector = LiveStatsCollector()
        snapshots = collector.monitor_listening(duration, interval)

        console.print(
            f"\n✅ Monitoring completed. Captured {len(snapshots)} snapshots."
        )

        # Show summary
        playing_snapshots = [s for s in snapshots if s.get("is_playing")]
        unique_tracks = set()

        for snapshot in playing_snapshots:
            track = snapshot.get("current_track")
            if track:
                unique_tracks.add(track["track_id"])

        console.print(f"📊 Summary:")
        console.print(
            f"  • Active listening time: {len(playing_snapshots) * interval / 60:.1f} minutes"
        )
        console.print(f"  • Unique tracks played: {len(unique_tracks)}")

    except KeyboardInterrupt:
        console.print("\n⏹️  Monitoring stopped by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error during monitoring: {e}", style="red")


@cli.command()
@click.option(
    "--format", "-f", type=click.Choice(["json"]), default="json", help="Export format"
)
def export(format):
    """Export your Spotify data."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Preparing data export...", total=None)

        try:
            # Get user info first
            auth = SpotifyAuthenticator()
            spotify = auth.authenticate()
            user_info = spotify.current_user()

            if not user_info:
                console.print("❌ Could not get user information", style="red")
                return

            # Initialize data manager and export
            data_manager = SpotifyDataManager()
            export_path = data_manager.export_user_data(user_info["id"], format)

            progress.remove_task(task)

            if export_path:
                console.print(
                    f"✅ Data exported successfully to: {export_path}", style="green"
                )
            else:
                console.print("❌ Export failed", style="red")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error exporting data: {e}", style="red")


@cli.command()
def auth():
    """Test Spotify authentication and display user info."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Authenticating with Spotify...", total=None)

        try:
            authenticator = SpotifyAuthenticator()
            spotify = authenticator.authenticate()
            user_info = authenticator.get_user_info()

            progress.remove_task(task)

            if user_info:
                console.print(
                    Panel(
                        f"✅ [bold green]Authentication Successful![/bold green]\n\n"
                        f"👤 User: {user_info.get('display_name', 'N/A')}\n"
                        f"🆔 ID: {user_info.get('id', 'N/A')}\n"
                        f"🌍 Country: {user_info.get('country', 'N/A')}\n"
                        f"👥 Followers: {user_info.get('followers', {}).get('total', 0):,}",
                        title="Spotify Account Info",
                        border_style="green",
                    )
                )
            else:
                console.print("❌ Authentication failed", style="red")

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Authentication error: {e}", style="red")


@cli.command()
def setup():
    """Guide for setting up Spotify API credentials."""
    setup_guide = """
[bold cyan]Spotify API Setup Guide[/bold cyan]

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
   - App Name: Spoticron (or any name you prefer)
   - App Description: Personal Spotify analytics tool
5. After creating the app, note down:
   - Client ID
   - Client Secret
6. In your app settings, add this redirect URI:
   - http://localhost:8080/callback

7. Create a .env file in this directory with:
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:8080/callback

8. Run 'spoticron auth' to test your setup
    """

    console.print(Panel(setup_guide, title="Setup Instructions", border_style="cyan"))


if __name__ == "__main__":
    cli()
