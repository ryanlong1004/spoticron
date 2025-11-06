# Spoticron - Spotify Analytics Tool

<div align="center">
  <img src="assets/spoticron.png" alt="Spoticron Logo" width="300"/>

[![GitHub release](https://img.shields.io/github/v/release/ryanlong1004/spoticron)](https://github.com/ryanlong1004/spoticron/releases)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Spotify API](https://img.shields.io/badge/Spotify-API-1DB954.svg)](https://developer.spotify.com/documentation/web-api/)

</div>

A comprehensive command-line tool for analyzing your Spotify listening habits with both live statistics and historical analysis.

## Features

- 🎵 **Live Stats**: Get real-time information about currently playing tracks
- 🕒 **Recent Activity**: View your recently played tracks
- 🏆 **Top Lists**: Analyze your top tracks and artists across different time periods
- � **Playlist Management**: View all your playlists and browse tracks in any playlist, including Liked Songs
- �📊 **Historical Analysis**: Deep dive into your listening evolution and patterns
- 🔍 **Discovery Patterns**: Track your music discovery habits
- 💾 **Data Export**: Export your listening data for further analysis
- 🎧 **Live Monitoring**: Real-time monitoring of your listening activity

## Quick Start

Get Spoticron running in under 5 minutes:

### Prerequisites

- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **Spotify account** (Free or Premium)
- **Git** ([Download here](https://git-scm.com/downloads))

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/ryanlong1004/spoticron.git
   cd spoticron
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify API** (2 minutes):

   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create an App" → Fill any name/description → Click "Create"
   - Copy your **Client ID** and **Client Secret**
   - In app settings, add redirect URI: `http://127.0.0.1:8080`

4. **Configure Spoticron**:

   ```bash
   cp .env.example .env
   # Edit .env with your Client ID and Client Secret
   ```

5. **Test it works**:
   ```bash
   python spoticron.py auth
   ```

🎉 **You're ready!** Try `python spoticron.py current` to see your currently playing track.

---

## Detailed Setup Guide

### Complete Installation

For users who prefer more detailed instructions:

1. **System Requirements**:

   - Python 3.8 or higher
   - Git (for cloning)
   - Internet connection
   - Spotify account (Free or Premium)

2. **Clone and Setup**:

   ```bash
   git clone https://github.com/ryanlong1004/spoticron.git
   cd spoticron
   pip install -r requirements.txt
   ```

3. **Create Spotify App** (if not done in Quick Start):
   - Follow the Spotify API Setup section below

### Spotify API Setup (Detailed)

## Spotify API Setup (Detailed)

If you need more detailed guidance for Spotify API setup:

1. **Visit** [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. **Log in** with your Spotify account
3. **Create App**:

   - Click "Create an App"
   - **App Name**: `Spoticron` (or any name)
   - **App Description**: `Personal Spotify analytics`
   - Check the boxes for Terms of Service
   - Click "Create"

4. **Get Your Credentials**:

   - On your app's page, you'll see **Client ID** (copy this)
   - Click "Show Client Secret" and copy the **Client Secret**
   - ⚠️ **Keep these private!** Don't share them publicly

5. **Set Redirect URI**:

   - Click "Edit Settings"
   - In "Redirect URIs", add: `http://127.0.0.1:8080`
   - Click "Add" then "Save"

6. **Configure Spoticron**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` file:

   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8080
   ```

### First Time Authentication

Run the auth command and follow the prompts:

```bash
python spoticron.py auth
```

This will:

1. Open your browser to Spotify's authorization page
2. Ask you to log in and grant permissions
3. Redirect to a page that may show "This site can't be reached" - **this is normal!**
4. Copy the entire URL from your browser's address bar
5. Paste it back into the terminal

✅ **Success!** You should see your Spotify username displayed.

## Usage & Examples

### Basic Commands

**Check what's currently playing**:

```bash
python spoticron.py current
```

<details>
<summary>📋 Example Output</summary>

```
♪ Now Playing ♪
🎵 Bohemian Rhapsody
👤 Queen
💿 A Night at the Opera
⏱️  2:35 / 5:55
📊 ████████░░░░░░░░░░ 45.2%
⭐ ⭐⭐⭐⭐☆ (85/100)
```

</details>

**View your recent listening history**:

```bash
python spoticron.py recent
```

<details>
<summary>📋 Example Output</summary>

```
🎵 Recently Played Tracks
┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Track              ┃ Artist             ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ Stairway to Heaven │ Led Zeppelin       │
│ 2  │ Hotel California   │ Eagles             │
│ 3  │ Sweet Child O Mine │ Guns N' Roses      │
└────┴────────────────────┴────────────────────┘
```

</details>

**Discover your top music**:

```bash
python spoticron.py top-tracks --time-range short_term
```

<details>
<summary>📋 Example Output</summary>

```
🏆 Top 10 Tracks - Last 4 Weeks
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank ┃ Track              ┃ Artist             ┃ Popularity ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1    │ Blinding Lights    │ The Weeknd         │ 88/100     │
│ 2    │ Levitating         │ Dua Lipa           │ 85/100     │
│ 3    │ Good 4 U           │ Olivia Rodrigo     │ 79/100     │
└──────┴────────────────────┴────────────────────┴────────────┘
```

**Time periods available:**

- `short_term`: Last 4 weeks (your current favorites)
- `medium_term`: Last 6 months (recent trends)
- `long_term`: All time (your classics)
</details>

**Browse your playlists**:

```bash
python spoticron.py playlists
```

<details>
<summary>📋 Example Output</summary>

```
📚 Your Playlists (25 total)
┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #  ┃ Name               ┃ Tracks ┃ Owner      ┃ Type       ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1  │ My Favorites       │ 234    │ You        │ Private    │
│ 2  │ Workout Mix        │ 89     │ You        │ Public     │
│ 3  │ Chill Vibes        │ 156    │ You        │ Public     │
└────┴────────────────────┴────────┴────────────┴────────────┘
```

</details>

**View all tracks in a playlist (including Liked Songs)**:

```bash
# View your Liked Songs
python spoticron.py playlist-tracks

# View tracks from a specific playlist
python spoticron.py playlist-tracks <playlist_id>

# Show detailed information
python spoticron.py playlist-tracks --detailed

# Export to JSON file
python spoticron.py playlist-tracks --export
```

<details>
<summary>📋 Example Output</summary>

```
🎵 Liked Songs (1,234 tracks)
┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Track              ┃ Artist(s)          ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ Bohemian Rhapsody  │ Queen              │
│ 2  │ Stairway to Heaven │ Led Zeppelin       │
│ 3  │ Hotel California   │ Eagles             │
└────┴────────────────────┴────────────────────┘

Summary:
• Total tracks: 1,234
• Total duration: 82.3 hours
• Average popularity: 76.5/100
• Explicit tracks: 89
```

**Tip**: Use the `playlists` command to find playlist IDs, or copy them from Spotify URLs.

</details>

### Advanced Features

<details>
<summary>🔬 <strong>Deep Analysis</strong> - Comprehensive listening insights</summary>

```bash
python spoticron.py analyze
python spoticron.py analyze --export  # Save results to JSON
```

Provides:

- **Listening Evolution**: How your taste has changed over time
- **Diversity Metrics**: Variety in your music selection
- **Mood Analysis**: Emotional patterns in your music
- **Discovery Patterns**: Rate of finding new music

</details>

<details>
<summary>👁️ <strong>Live Monitoring</strong> - Real-time listening tracker</summary>

```bash
python spoticron.py monitor --duration 10 --interval 30
```

Monitors your listening activity in real-time:

- Track what you're listening to every 30 seconds
- Run for 10 minutes (or any duration you choose)
- Perfect for understanding your listening sessions

</details>

<details>
<summary>💾 <strong>Data Export</strong> - Backup your listening data</summary>

```bash
python spoticron.py export
```

Exports your complete listening history to JSON format for:

- Personal backups
- Data analysis in other tools
- Long-term archival
- Privacy control

</details>

### Getting Help

**View setup guide**:

```bash
python spoticron.py setup
```

**Show help for any command**:

```bash
python spoticron.py --help
python spoticron.py current --help
```

---

## Troubleshooting

### Common First-Time Issues

<details>
<summary>🚫 <strong>"Invalid client" or authentication errors</strong></summary>

**Problem**: `Invalid client` or `INVALID_CLIENT: Invalid redirect URI`

**Solutions**:

1. **Check your credentials**: Verify Client ID and Client Secret are copied correctly (no extra spaces)
2. **Verify redirect URI**: Must be exactly `http://127.0.0.1:8080` in both Spotify dashboard and `.env` file
3. **Case sensitivity**: Make sure there are no typos in your `.env` file variable names
4. **Restart**: Try running `python spoticron.py auth` again

</details>

<details>
<summary>🔗 <strong>"This site can't be reached" after Spotify login</strong></summary>

**Problem**: Browser shows error page after Spotify authorization

**This is normal!** Just copy the URL from your browser's address bar and paste it back into the terminal. The URL contains the authorization code Spoticron needs.

</details>

<details>
<summary>📁 <strong>"Permission denied" or file errors</strong></summary>

**Problem**: Can't create files or access database

**Solutions**:

1. **Check permissions**: Make sure you can write to the current directory
2. **Create data directory**: `mkdir -p data/cache data/exports data/backups`
3. **Run from project root**: Make sure you're in the `spoticron/` directory when running commands

</details>

<details>
<summary>🎵 <strong>"No current track" or empty results</strong></summary>

**Problem**: Commands return no data

**Reasons**:

- **Nothing playing**: Start playing music on Spotify first
- **Private session**: Disable private session in Spotify settings
- **Account type**: Some features require Spotify Premium
- **Recent activity**: Recent tracks only shows last 50 plays

</details>

<details>
<summary>🐍 <strong>Python or pip issues</strong></summary>

**Problem**: `python` command not found or version issues

**Solutions**:

1. **Check Python version**: `python --version` (need 3.8+)
2. **Try python3**: Use `python3` instead of `python`
3. **Virtual environment**: Consider using `python -m venv venv` then `source venv/bin/activate`
4. **Install Python**: Visit [python.org](https://www.python.org/downloads/)

</details>

### Getting More Help

1. **Check this troubleshooting section** for common issues
2. **Review the [Spotify API documentation](https://developer.spotify.com/documentation/web-api/)**
3. **Open an issue** on the GitHub repository with:
   - Your error message
   - Your Python version (`python --version`)
   - Steps you tried

---

## Technical Details

### Data Storage

Spoticron stores your data locally in:

- **Database**: SQLite database at `data/spoticron.db`
- **Cache**: Token cache in `data/cache/`
- **Exports**: Data exports in `data/exports/`
- **Backups**: Database backups in `data/backups/`

### Privacy and Data

- **Local storage only**: All data stays on your machine
- **No external servers**: Only communicates with Spotify's official API
- **Full control**: Delete everything by removing the `data/` directory
- **Readable exports**: JSON format for transparency
- **Secure authentication**: Uses industry-standard OAuth 2.0

### Features in Detail

<details>
<summary><strong>Live Statistics</strong></summary>

- **Current Track**: Real-time information about what's playing
- **Recent History**: Last 50 played tracks with timestamps
- **Progress Tracking**: Visual progress bars and playback position
- **Rich Formatting**: Beautiful terminal output with colors and symbols

</details>

<details>
<summary><strong>Historical Analysis</strong></summary>

- **Evolution Analysis**: How your music taste has changed over time periods
- **Diversity Metrics**: Mathematical analysis of your listening variety
- **Mood Analysis**: Emotional patterns based on Spotify's audio features
- **Discovery Patterns**: Rate and frequency of finding new music
- **Trend Detection**: Identify patterns in your listening behavior

</details>

<details>
<summary><strong>Data Management</strong></summary>

- **Automatic Persistence**: Seamless background data storage
- **Multiple Export Formats**: JSON exports for data portability
- **Database Backups**: Automatic backup system for data safety
- **Cleanup Utilities**: Tools to manage and organize your data
- **Migration Support**: Easy data transfer between installations

</details>

## Project Structure

```
spoticron/
├── src/
│   ├── auth.py              # Spotify authentication
│   ├── live_stats.py        # Live statistics collection
│   ├── historical_stats.py  # Historical analysis
│   ├── data_storage.py      # Data persistence
│   └── utils.py            # Utility functions
├── tests/                  # Unit tests
├── data/                   # Data directory (created automatically)
│   ├── cache/              # Token cache
│   ├── exports/            # Data exports
│   └── backups/            # Database backups
├── spoticron.py           # Main CLI interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Dependencies

Core dependencies (automatically installed):

- **spotipy**: Spotify Web API wrapper
- **click**: Command-line interface creation
- **rich**: Beautiful terminal formatting
- **sqlalchemy**: Database ORM
- **python-dotenv**: Environment variable management

Development dependencies are separate in `requirements-dev.txt`.

## Troubleshooting

### Authentication Issues

- Verify your Client ID and Client Secret are correct
- Ensure the redirect URI matches exactly: `http://127.0.0.1:8080`
- Check that your app has the necessary scopes enabled

### Permission Errors

- Make sure the `data/` directory is writable
- Check file permissions for the SQLite database

### Missing Data

- Some endpoints require premium Spotify accounts
- Recent tracks are limited to the last 50 plays
- Historical data depends on your Spotify usage

## Privacy and Data

- All data is stored locally on your machine
- No data is sent to external servers (except Spotify's API)
- You can delete all stored data by removing the `data/` directory
- Exports are in human-readable JSON format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [spotipy library](https://spotipy.readthedocs.io/)
- [Rich library](https://rich.readthedocs.io/) for beautiful terminal output

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the [Spotify API documentation](https://developer.spotify.com/documentation/web-api/)
3. Open an issue on the repository

---

**Happy listening! 🎵**
