# Spoticron - Spotify Analytics Tool

A comprehensive command-line tool for analyzing your Spotify listening habits with both live statistics and historical analysis.

## Features

- 🎵 **Live Stats**: Get real-time information about currently playing tracks
- 🕒 **Recent Activity**: View your recently played tracks
- 🏆 **Top Lists**: Analyze your top tracks and artists across different time periods
- 📊 **Historical Analysis**: Deep dive into your listening evolution and patterns
- 🔍 **Discovery Patterns**: Track your music discovery habits
- 💾 **Data Export**: Export your listening data for further analysis
- 🎧 **Live Monitoring**: Real-time monitoring of your listening activity

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd spoticron
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
   - **App Name**: Spoticron (or any name you prefer)
   - **App Description**: Personal Spotify analytics tool
5. After creating the app, note down your **Client ID** and **Client Secret**
6. In your app settings, add this redirect URI: `http://localhost:8080/callback`

## Configuration

1. **Copy the example environment file**:

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your Spotify credentials**:

   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:8080/callback
   ```

3. **Test your setup**:
   ```bash
   python spoticron.py auth
   ```

## Usage

### Basic Commands

**Show currently playing track**:

```bash
python spoticron.py current
python spoticron.py current --show-details  # Detailed view
```

**View recent tracks**:

```bash
python spoticron.py recent
python spoticron.py recent --limit 20 --detailed
```

**Get top tracks and artists**:

```bash
python spoticron.py top-tracks --time-range short_term
python spoticron.py top-artists --time-range medium_term
```

Time ranges:

- `short_term`: Last 4 weeks
- `medium_term`: Last 6 months
- `long_term`: All time

### Advanced Analysis

**Comprehensive historical analysis**:

```bash
python spoticron.py analyze
python spoticron.py analyze --export  # Save results to JSON
```

**Monitor listening activity**:

```bash
python spoticron.py monitor --duration 10 --interval 30
```

**Export your data**:

```bash
python spoticron.py export
```

### Help and Setup

**View setup guide**:

```bash
python spoticron.py setup
```

**Show help for any command**:

```bash
python spoticron.py --help
python spoticron.py current --help
```

## Data Storage

Spoticron stores your data locally in:

- **Database**: SQLite database at `data/spoticron.db`
- **Cache**: Token cache in `data/cache/`
- **Exports**: Data exports in `data/exports/`
- **Backups**: Database backups in `data/backups/`

## Features in Detail

### Live Statistics

- Current playing track with detailed information
- Recently played tracks with timestamps
- Real-time monitoring capabilities

### Historical Analysis

- **Evolution Analysis**: How your music taste has changed over time
- **Diversity Metrics**: Measure of how diverse your listening habits are
- **Mood Analysis**: Analyze the mood of your music based on audio features
- **Discovery Patterns**: Track how often you discover new music

### Data Management

- Automatic data persistence
- Export capabilities (JSON format)
- Database backups
- Data cleanup utilities

## Project Structure

```
spoticron/
├── src/
│   ├── auth.py              # Spotify authentication
│   ├── live_stats.py        # Live statistics collection
│   ├── historical_stats.py  # Historical analysis
│   └── data_storage.py      # Data persistence
├── data/                    # Data directory
│   ├── cache/              # Token cache
│   ├── exports/            # Data exports
│   └── backups/            # Database backups
├── config/                 # Configuration files
├── tests/                  # Unit tests
├── spoticron.py           # Main CLI interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Dependencies

- **spotipy**: Spotify Web API wrapper
- **click**: Command-line interface creation
- **rich**: Rich text and beautiful formatting
- **sqlalchemy**: Database ORM
- **pandas**: Data analysis
- **python-dotenv**: Environment variable management

## Troubleshooting

### Authentication Issues

- Verify your Client ID and Client Secret are correct
- Ensure the redirect URI matches exactly: `http://localhost:8080/callback`
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
