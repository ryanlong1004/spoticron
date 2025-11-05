#!/usr/bin/env python3
"""
Spoticron - Spotify Analytics CLI
Command-line interface for Spotify listening statistics and analysis.
"""

import click
import json
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

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
    from rich.align import Align
    from rich.text import Text

    subtitle = Text("Spotify Analytics & Insights Tool", style="italic bright_white")

    console.print()
    console.print(
        Panel(
            Align.center(subtitle),
            border_style="bright_green",
            padding=(1, 2),
            title="[bold bright_white]SPOTICRON[/bold bright_white]",
            title_align="center",
        )
    )
    console.print()


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
def current():
    """Show currently playing track information."""
    console.print("🎵 Getting current track...", style="dim")

    try:
        collector = LiveStatsCollector()
        current_track = collector.get_current_track()

        if current_track:
            print_current_track(current_track)
        else:
            console.print("🔇 No track currently playing", style="yellow")

    except Exception as e:
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
            console.print()  # Add clean line break

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

                console.print("\n🔍 [bold]Discovery Patterns[/bold]")
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
@click.option(
    "--duration",
    "-d",
    default=0,
    help="Duration to monitor in minutes (default: 0 = indefinite)",
)
@click.option(
    "--interval",
    "-i",
    default=5,
    help="Update interval in seconds (default: 5)",
)
@click.option(
    "--previous-tracks",
    "-p",
    default=3,
    help="Number of previous tracks to show (default: 3)",
)
@click.option(
    "--next-tracks",
    "-n",
    default=3,
    help="Number of upcoming tracks to show (default: 3)",
)
def monitor(duration, interval, previous_tracks, next_tracks):
    """Enhanced monitoring mode with smart updates and queue display. Default: indefinite monitoring."""
    show_banner()

    try:
        live_stats = LiveStatsCollector()

        console.print("🎵 Starting enhanced monitoring mode...", style="bold green")
        if duration == 0:
            console.print("⏱️  Duration: Indefinite (Ctrl+C to stop)")
        else:
            console.print(f"⏱️  Duration: {duration} minutes")
        console.print(f"🔄 Update interval: {interval} seconds")
        console.print(f"📜 Previous tracks: {previous_tracks}")
        console.print(f"⏭️  Next tracks: {next_tracks}")
        console.print("")

        live_stats.monitor_enhanced(
            duration_minutes=duration,
            interval_seconds=interval,
            previous_tracks=previous_tracks,
            next_tracks=next_tracks,
        )

    except KeyboardInterrupt:
        console.print("\n🛑 Monitoring stopped by user", style="bold red")
    except Exception as e:
        console.print(f"❌ Monitoring error: {e}", style="red")


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Export format (default: json)",
)
@click.option(
    "--output",
    "-o",
    help="Output file path (optional - will auto-generate if not provided)",
)
@click.option(
    "--data-type",
    "-t",
    type=click.Choice(["all", "listening-history", "top-tracks", "top-artists"]),
    default="all",
    help="Type of data to export (default: all)",
)
@click.option(
    "--days",
    "-d",
    type=int,
    help="Number of days of listening history to export (optional - exports all if not specified)",
)
def export(format, output, data_type, days):
    """Export your Spotify data to a file.

    Examples:
    \b
      spoticron export                           # Export all data as JSON
      spoticron export -f csv                    # Export all data as CSV
      spoticron export -t listening-history      # Export only listening history
      spoticron export -d 30                     # Export last 30 days of data
      spoticron export -o my_data.json          # Export to specific file
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Preparing data export...", total=None)

        try:
            # Get user info first
            progress.update(task, description="Authenticating with Spotify...")
            auth = SpotifyAuthenticator()
            spotify = auth.authenticate()
            user_info = spotify.current_user()

            if not user_info:
                progress.remove_task(task)
                console.print("❌ Could not get user information", style="red")
                console.print("💡 Try running 'spoticron auth' to test your connection")
                return

            user_id = user_info["id"]
            console.print(
                f"👤 Exporting data for user: {user_info.get('display_name', user_id)}"
            )

            # Initialize data manager and export
            progress.update(task, description="Initializing data manager...")
            data_manager = SpotifyDataManager()

            progress.update(task, description="Collecting data for export...")

            # For now, we'll export all data regardless of data_type
            # TODO: Implement selective data export in future versions
            if data_type != "all":
                console.print(
                    f"⚠️  Note: Selective export for '{data_type}' not yet implemented.",
                    style="yellow",
                )
                console.print("📋 Exporting all available data instead.")

            if days:
                console.print(
                    f"⚠️  Note: Date filtering for last {days} days not yet implemented.",
                    style="yellow",
                )
                console.print("📋 Exporting all available data instead.")

            export_path = data_manager.export_user_data(user_id, format)

            progress.remove_task(task)

            if export_path:
                # Check if custom output path was specified
                if output:
                    from shutil import move
                    from pathlib import Path

                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    move(export_path, output_path)
                    export_path = str(output_path)

                console.print("✅ Data exported successfully!", style="green")
                console.print(f"📁 File location: {export_path}")

                # Show file size
                file_size = Path(export_path).stat().st_size
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size} bytes"

                console.print(f"📊 File size: {size_str}")
            else:
                # If export failed, try to collect fresh data from Spotify API
                console.print(
                    "⚠️  No stored data found. Collecting fresh data from Spotify...",
                    style="yellow",
                )

                progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                )

                with progress:
                    fresh_task = progress.add_task(
                        "Collecting current Spotify data...", total=None
                    )

                    try:
                        # Collect fresh data from Spotify API
                        fresh_data = {
                            "user_info": user_info,
                            "current_track": None,
                            "recent_tracks": [],
                            "top_tracks": {},
                            "top_artists": {},
                            "export_timestamp": datetime.now().isoformat(),
                            "data_source": "live_api_collection",
                        }

                        # Get current track
                        try:
                            from src.live_stats import LiveStatsCollector

                            collector = LiveStatsCollector()
                            current = collector.get_current_track()
                            if current:
                                fresh_data["current_track"] = {
                                    "track_name": current.track_name,
                                    "artist_names": current.artist_names,
                                    "album_name": current.album_name,
                                    "progress_ms": current.progress_ms,
                                    "duration_ms": current.duration_ms,
                                    "is_playing": current.is_playing,
                                }
                        except Exception:
                            pass

                        # Get recent tracks
                        try:
                            recent = collector.get_recently_played(20)
                            fresh_data["recent_tracks"] = [
                                {
                                    "track_name": track.track_name,
                                    "artist_names": track.artist_names,
                                    "album_name": track.album_name,
                                    "played_at": track.played_at,
                                }
                                for track in recent
                            ]
                        except Exception:
                            pass

                        # Get top tracks for different time ranges
                        for time_range in ["short_term", "medium_term", "long_term"]:
                            try:
                                top_tracks = collector.get_top_tracks(time_range, 20)
                                fresh_data["top_tracks"][time_range] = [
                                    {
                                        "name": track.name,
                                        "artist_names": track.artist_names,
                                        "popularity": track.popularity,
                                    }
                                    for track in top_tracks
                                ]
                            except Exception:
                                fresh_data["top_tracks"][time_range] = []

                        # Get top artists for different time ranges
                        for time_range in ["short_term", "medium_term", "long_term"]:
                            try:
                                top_artists = collector.get_top_artists(time_range, 20)
                                fresh_data["top_artists"][time_range] = [
                                    {
                                        "name": artist.name,
                                        "genres": artist.genres,
                                        "popularity": artist.popularity,
                                        "followers": artist.followers,
                                    }
                                    for artist in top_artists
                                ]
                            except Exception:
                                fresh_data["top_artists"][time_range] = []

                        progress.remove_task(fresh_task)

                        # Generate filename and save
                        from pathlib import Path

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"spotify_live_export_{user_id}_{timestamp}.{format}"
                        if output:
                            export_path = Path(output)
                        else:
                            export_path = Path("data/exports") / filename

                        export_path.parent.mkdir(parents=True, exist_ok=True)

                        if format.lower() == "json":
                            with open(export_path, "w", encoding="utf-8") as f:
                                json.dump(fresh_data, f, indent=2, ensure_ascii=False)
                        else:
                            console.print(
                                "❌ CSV format not yet supported for live export",
                                style="red",
                            )
                            return

                        console.print(
                            "✅ Live data exported successfully!", style="green"
                        )
                        console.print(f"📁 File location: {export_path}")
                        console.print(
                            "💡 This export contains current data from Spotify API"
                        )
                        console.print(
                            "💡 For historical data, run monitoring first: 'spoticron monitor -d 5'"
                        )

                        # Show file size
                        file_size = export_path.stat().st_size
                        if file_size > 1024 * 1024:
                            size_str = f"{file_size / (1024 * 1024):.1f} MB"
                        elif file_size > 1024:
                            size_str = f"{file_size / 1024:.1f} KB"
                        else:
                            size_str = f"{file_size} bytes"

                        console.print(f"📊 File size: {size_str}")

                    except Exception as fresh_error:
                        progress.remove_task(fresh_task)
                        console.print(
                            "❌ Failed to collect fresh data from Spotify", style="red"
                        )
                        console.print(f"❌ Error: {fresh_error}", style="red")
                        console.print("💡 This might happen if:")
                        console.print("   • No active Spotify session")
                        console.print("   • API rate limits exceeded")
                        console.print("   • Network connectivity issues")
                        console.print(
                            "💡 Try running 'spoticron current' to test your connection"
                        )

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Error exporting data: {e}", style="red")
            console.print(
                "💡 For detailed error information, check your Spotify API credentials"
            )
            console.print("💡 Run 'spoticron auth' to verify your connection")


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
            authenticator.authenticate()
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
   - https://localhost:8080/callback

7. Create a .env file in this directory with:
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=https://localhost:8080/callback

8. Run 'spoticron auth' to test your setup
    """

    console.print(Panel(setup_guide, title="Setup Instructions", border_style="cyan"))


if __name__ == "__main__":
    cli()
