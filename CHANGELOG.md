# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added
- Initial release of Spoticron
- Spotify OAuth2 authentication with automatic token refresh
- Live statistics collection:
  - Current playing track information
  - Recently played tracks
  - Real-time listening monitoring
- Top tracks and artists analysis for different time periods:
  - Short term (last 4 weeks)
  - Medium term (last 6 months)  
  - Long term (all time)
- Historical analysis features:
  - Listening evolution tracking
  - Music diversity metrics
  - Mood analysis based on audio features
  - Discovery pattern analysis
- Data persistence with SQLite database
- Data export capabilities (JSON format)
- Command-line interface with rich formatting
- Comprehensive documentation and setup guide
- Basic test suite
- Database backup and cleanup utilities

### Security
- Local-only data storage (no external data transmission except to Spotify API)
- Secure token management with automatic refresh
- Environment variable configuration for sensitive credentials

## [Unreleased]

### Planned Features
- CSV export format
- Advanced visualization capabilities
- Playlist analysis
- Social sharing features
- Web dashboard interface
- Enhanced mood analysis
- Genre trend analysis
- Collaborative filtering recommendations

---

For more details about any release, see the corresponding GitHub release notes.