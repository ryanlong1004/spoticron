"""
Historical stats module for analyzing Spotify listening patterns over time.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter

import spotipy
from .auth import SpotifyAuthenticator


@dataclass
class ListeningPeriod:
    """Data class for listening statistics over a period."""

    start_date: str
    end_date: str
    total_tracks: int
    unique_tracks: int
    unique_artists: int
    unique_albums: int
    total_listening_time_ms: int
    top_tracks: List[Dict[str, Any]]
    top_artists: List[Dict[str, Any]]
    top_genres: List[Tuple[str, int]]
    listening_patterns: Dict[str, Any]


@dataclass
class GenreAnalysis:
    """Data class for genre analysis."""

    genre: str
    track_count: int
    artist_count: int
    percentage: float
    representative_artists: List[str]


@dataclass
class ArtistEvolution:
    """Data class for tracking artist popularity over time."""

    artist_name: str
    artist_id: str
    periods: List[Dict[str, Any]]  # Each period has date_range, play_count, rank


class HistoricalStatsAnalyzer:
    """Analyzes historical Spotify data and listening patterns."""

    def __init__(self, spotify_client: Optional[spotipy.Spotify] = None):
        """
        Initialize the historical stats analyzer.

        Args:
            spotify_client: Authenticated Spotify client.
        """
        if spotify_client is None:
            auth = SpotifyAuthenticator()
            spotify_client = auth.authenticate()

        self.spotify = spotify_client

    def get_comprehensive_top_data(
        self, time_ranges: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive top tracks and artists data for multiple time ranges.

        Args:
            time_ranges: List of time ranges to analyze.

        Returns:
            Dictionary with comprehensive top data.
        """
        if time_ranges is None:
            time_ranges = ["short_term", "medium_term", "long_term"]

        comprehensive_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "time_ranges": {},
        }

        for time_range in time_ranges:
            try:
                # Get top tracks
                top_tracks = self.spotify.current_user_top_tracks(
                    time_range=time_range, limit=50
                )

                # Get top artists
                top_artists = self.spotify.current_user_top_artists(
                    time_range=time_range, limit=50
                )

                # Process and enrich data
                tracks_data = self._process_top_tracks(top_tracks["items"])
                artists_data = self._process_top_artists(top_artists["items"])

                comprehensive_data["time_ranges"][time_range] = {
                    "tracks": tracks_data,
                    "artists": artists_data,
                    "genres": self._extract_genres_from_artists(top_artists["items"]),
                    "audio_features": self._get_audio_features_summary(
                        [track["id"] for track in top_tracks["items"]]
                    ),
                }

            except Exception as e:
                print(f"Error getting data for {time_range}: {e}")
                comprehensive_data["time_ranges"][time_range] = None

        return comprehensive_data

    def analyze_listening_evolution(self) -> Dict[str, Any]:
        """
        Analyze how listening preferences have evolved over time.

        Returns:
            Dictionary with evolution analysis.
        """
        evolution_data = {}
        time_ranges = ["short_term", "medium_term", "long_term"]
        range_labels = ["Last Month", "Last 6 Months", "All Time"]

        # Get data for all time ranges
        all_data = self.get_comprehensive_top_data(time_ranges)

        # Analyze artist evolution
        artist_evolution = self._analyze_artist_evolution(all_data)

        # Analyze genre evolution
        genre_evolution = self._analyze_genre_evolution(all_data)

        # Analyze audio features evolution
        audio_evolution = self._analyze_audio_features_evolution(all_data)

        evolution_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "artist_evolution": artist_evolution,
            "genre_evolution": genre_evolution,
            "audio_features_evolution": audio_evolution,
            "time_range_labels": dict(zip(time_ranges, range_labels)),
        }

        return evolution_data

    def get_discovery_patterns(self) -> Dict[str, Any]:
        """
        Analyze music discovery patterns.

        Returns:
            Dictionary with discovery analysis.
        """
        try:
            # Get recently played tracks for discovery analysis
            recent_tracks = self.spotify.current_user_recently_played(limit=50)

            # Get top tracks for comparison
            top_tracks_short = self.spotify.current_user_top_tracks(
                time_range="short_term", limit=50
            )

            top_track_ids = {track["id"] for track in top_tracks_short["items"]}

            discovery_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_recent_tracks": len(recent_tracks["items"]),
                "new_discoveries": [],
                "rediscovered_tracks": [],
                "discovery_rate": 0.0,
            }

            new_discoveries = []
            rediscovered = []

            for item in recent_tracks["items"]:
                track = item["track"]
                if track["id"] not in top_track_ids:
                    new_discoveries.append(
                        {
                            "track_name": track["name"],
                            "artist_names": [
                                artist["name"] for artist in track["artists"]
                            ],
                            "played_at": item["played_at"],
                            "popularity": track.get("popularity", 0),
                            "preview_url": track.get("preview_url"),
                        }
                    )
                else:
                    rediscovered.append(
                        {
                            "track_name": track["name"],
                            "artist_names": [
                                artist["name"] for artist in track["artists"]
                            ],
                            "played_at": item["played_at"],
                        }
                    )

            discovery_data["new_discoveries"] = new_discoveries
            discovery_data["rediscovered_tracks"] = rediscovered
            discovery_data["discovery_rate"] = (
                len(new_discoveries) / len(recent_tracks["items"]) * 100
                if recent_tracks["items"]
                else 0
            )

            return discovery_data

        except Exception as e:
            print(f"Error analyzing discovery patterns: {e}")
            return {}

    def analyze_listening_diversity(self) -> Dict[str, Any]:
        """
        Analyze the diversity of listening habits.

        Returns:
            Dictionary with diversity metrics.
        """
        try:
            comprehensive_data = self.get_comprehensive_top_data()

            diversity_metrics = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "time_ranges": {},
            }

            for time_range, data in comprehensive_data["time_ranges"].items():
                if not data:
                    continue

                tracks = data["tracks"]
                genres = data["genres"]

                # Calculate diversity metrics
                unique_artists = len(
                    set(
                        artist_id
                        for track in tracks
                        for artist_id in track.get("artist_ids", [])
                    )
                )

                unique_genres = len(genres)

                # Genre distribution entropy (measure of diversity)
                genre_entropy = self._calculate_entropy([count for _, count in genres])

                # Artist distribution (how concentrated listening is)
                artist_play_distribution = Counter()
                for track in tracks:
                    for artist_name in track.get("artist_names", []):
                        artist_play_distribution[artist_name] += 1

                artist_entropy = self._calculate_entropy(
                    list(artist_play_distribution.values())
                )

                # Audio features diversity
                audio_features = data.get("audio_features", {})
                feature_diversity = self._calculate_audio_feature_diversity(
                    audio_features
                )

                diversity_metrics["time_ranges"][time_range] = {
                    "unique_artists": unique_artists,
                    "unique_genres": unique_genres,
                    "genre_entropy": genre_entropy,
                    "artist_entropy": artist_entropy,
                    "audio_feature_diversity": feature_diversity,
                    "top_genre_dominance": (
                        genres[0][1] / sum(count for _, count in genres) * 100
                        if genres
                        else 0
                    ),
                }

            return diversity_metrics

        except Exception as e:
            print(f"Error analyzing listening diversity: {e}")
            return {}

    def get_mood_analysis(self) -> Dict[str, Any]:
        """
        Analyze mood patterns based on audio features.

        Returns:
            Dictionary with mood analysis.
        """
        try:
            comprehensive_data = self.get_comprehensive_top_data()

            mood_analysis = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "time_ranges": {},
            }

            for time_range, data in comprehensive_data["time_ranges"].items():
                if not data or not data.get("audio_features"):
                    continue

                audio_features = data["audio_features"]

                # Define mood categories based on audio features
                mood_scores = self._calculate_mood_scores(audio_features)

                mood_analysis["time_ranges"][time_range] = {
                    "mood_scores": mood_scores,
                    "dominant_mood": max(mood_scores, key=mood_scores.get),
                    "energy_level": audio_features.get("avg_energy", 0),
                    "happiness_level": audio_features.get("avg_valence", 0),
                    "danceability": audio_features.get("avg_danceability", 0),
                }

            return mood_analysis

        except Exception as e:
            print(f"Error analyzing mood patterns: {e}")
            return {}

    def _process_top_tracks(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enrich top tracks data."""
        processed_tracks = []

        for i, track in enumerate(tracks):
            processed_track = {
                "rank": i + 1,
                "track_name": track["name"],
                "track_id": track["id"],
                "artist_names": [artist["name"] for artist in track["artists"]],
                "artist_ids": [artist["id"] for artist in track["artists"]],
                "album_name": track["album"]["name"],
                "album_id": track["album"]["id"],
                "duration_ms": track["duration_ms"],
                "popularity": track.get("popularity", 0),
                "explicit": track.get("explicit", False),
                "preview_url": track.get("preview_url"),
                "external_urls": track.get("external_urls", {}),
                "release_date": track["album"].get("release_date", ""),
                "album_type": track["album"].get("album_type", ""),
            }
            processed_tracks.append(processed_track)

        return processed_tracks

    def _process_top_artists(
        self, artists: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process and enrich top artists data."""
        processed_artists = []

        for i, artist in enumerate(artists):
            processed_artist = {
                "rank": i + 1,
                "artist_name": artist["name"],
                "artist_id": artist["id"],
                "genres": artist.get("genres", []),
                "popularity": artist.get("popularity", 0),
                "followers": artist["followers"]["total"],
                "external_urls": artist.get("external_urls", {}),
                "images": artist.get("images", []),
            }
            processed_artists.append(processed_artist)

        return processed_artists

    def _extract_genres_from_artists(
        self, artists: List[Dict[str, Any]]
    ) -> List[Tuple[str, int]]:
        """Extract and count genres from artists."""
        genre_counter = Counter()

        for artist in artists:
            for genre in artist.get("genres", []):
                genre_counter[genre] += 1

        return genre_counter.most_common()

    def _get_audio_features_summary(self, track_ids: List[str]) -> Dict[str, float]:
        """Get summarized audio features for a list of tracks."""
        try:
            if not track_ids:
                return {}

            audio_features = self.spotify.audio_features(track_ids)

            # Filter out None values
            valid_features = [f for f in audio_features if f is not None]

            if not valid_features:
                return {}

            # Calculate averages for numeric features
            feature_keys = [
                "danceability",
                "energy",
                "loudness",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
            ]

            summary = {}
            for key in feature_keys:
                values = [f[key] for f in valid_features if f.get(key) is not None]
                if values:
                    summary[f"avg_{key}"] = sum(values) / len(values)

            return summary

        except Exception as e:
            print(f"Error getting audio features: {e}")
            return {}

    def _analyze_artist_evolution(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how artist preferences have evolved."""
        evolution = {
            "stable_favorites": [],
            "rising_artists": [],
            "declining_artists": [],
            "new_discoveries": [],
        }

        time_ranges = ["long_term", "medium_term", "short_term"]

        # Get artist rankings for each time period
        artist_rankings = {}
        for time_range in time_ranges:
            data = all_data["time_ranges"].get(time_range)
            if data and data.get("artists"):
                artist_rankings[time_range] = {
                    artist["artist_id"]: {
                        "rank": artist["rank"],
                        "name": artist["artist_name"],
                    }
                    for artist in data["artists"]
                }

        # Analyze evolution patterns
        long_term_artists = set(artist_rankings.get("long_term", {}).keys())
        medium_term_artists = set(artist_rankings.get("medium_term", {}).keys())
        short_term_artists = set(artist_rankings.get("short_term", {}).keys())

        # Stable favorites (in all time ranges)
        stable_artists = long_term_artists & medium_term_artists & short_term_artists
        for artist_id in stable_artists:
            artist_name = artist_rankings["long_term"][artist_id]["name"]
            evolution["stable_favorites"].append(
                {
                    "name": artist_name,
                    "id": artist_id,
                    "long_term_rank": artist_rankings["long_term"][artist_id]["rank"],
                    "medium_term_rank": artist_rankings["medium_term"][artist_id][
                        "rank"
                    ],
                    "short_term_rank": artist_rankings["short_term"][artist_id]["rank"],
                }
            )

        # New discoveries (only in short term)
        new_artists = short_term_artists - medium_term_artists - long_term_artists
        for artist_id in new_artists:
            if artist_id in artist_rankings.get("short_term", {}):
                artist_name = artist_rankings["short_term"][artist_id]["name"]
                evolution["new_discoveries"].append(
                    {
                        "name": artist_name,
                        "id": artist_id,
                        "short_term_rank": artist_rankings["short_term"][artist_id][
                            "rank"
                        ],
                    }
                )

        return evolution

    def _analyze_genre_evolution(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how genre preferences have evolved."""
        genre_evolution = {}

        for time_range, data in all_data["time_ranges"].items():
            if data and data.get("genres"):
                total_genre_count = sum(count for _, count in data["genres"])
                genre_percentages = [
                    {
                        "genre": genre,
                        "count": count,
                        "percentage": (count / total_genre_count) * 100,
                    }
                    for genre, count in data["genres"][:10]  # Top 10 genres
                ]
                genre_evolution[time_range] = genre_percentages

        return genre_evolution

    def _analyze_audio_features_evolution(
        self, all_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze how audio feature preferences have evolved."""
        audio_evolution = {}

        for time_range, data in all_data["time_ranges"].items():
            if data and data.get("audio_features"):
                audio_evolution[time_range] = data["audio_features"]

        return audio_evolution

    def _calculate_entropy(self, values: List[int]) -> float:
        """Calculate entropy for diversity measurement."""
        if not values:
            return 0.0

        total = sum(values)
        if total == 0:
            return 0.0

        entropy = 0.0
        for value in values:
            if value > 0:
                probability = value / total
                entropy -= probability * (probability.bit_length() - 1)

        return entropy

    def _calculate_audio_feature_diversity(
        self, audio_features: Dict[str, float]
    ) -> float:
        """Calculate diversity score based on audio features."""
        if not audio_features:
            return 0.0

        # Normalize features to 0-1 range and calculate variance
        features = ["avg_danceability", "avg_energy", "avg_valence", "avg_acousticness"]

        feature_values = []
        for feature in features:
            if feature in audio_features:
                feature_values.append(audio_features[feature])

        if not feature_values:
            return 0.0

        # Calculate coefficient of variation as diversity measure
        mean_val = sum(feature_values) / len(feature_values)
        if mean_val == 0:
            return 0.0

        variance = sum((x - mean_val) ** 2 for x in feature_values) / len(
            feature_values
        )
        std_dev = variance**0.5

        return std_dev / mean_val  # Coefficient of variation

    def _calculate_mood_scores(
        self, audio_features: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate mood scores based on audio features."""
        moods = {
            "energetic": 0.0,
            "happy": 0.0,
            "chill": 0.0,
            "melancholic": 0.0,
            "danceable": 0.0,
        }

        if not audio_features:
            return moods

        # Define mood calculations based on audio features
        energy = audio_features.get("avg_energy", 0)
        valence = audio_features.get("avg_valence", 0)
        danceability = audio_features.get("avg_danceability", 0)
        acousticness = audio_features.get("avg_acousticness", 0)

        moods["energetic"] = energy * 100
        moods["happy"] = valence * 100
        moods["chill"] = acousticness * 100
        moods["melancholic"] = (1 - valence) * 100
        moods["danceable"] = danceability * 100

        return moods


def export_historical_data(data: Dict[str, Any], filename: str):
    """
    Export historical data to JSON file.

    Args:
        data: Data to export.
        filename: Output filename.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data exported to {filename}")
    except Exception as e:
        print(f"Error exporting data: {e}")


def format_evolution_summary(evolution_data: Dict[str, Any]) -> str:
    """
    Format evolution analysis as readable summary.

    Args:
        evolution_data: Evolution analysis data.

    Returns:
        Formatted summary string.
    """
    summary = []
    summary.append("🔄 LISTENING EVOLUTION SUMMARY")
    summary.append("=" * 50)

    # Artist evolution
    artist_evo = evolution_data.get("artist_evolution", {})
    if artist_evo.get("stable_favorites"):
        summary.append(
            f"\n🌟 Stable Favorites ({len(artist_evo['stable_favorites'])} artists):"
        )
        for artist in artist_evo["stable_favorites"][:5]:
            summary.append(f"  • {artist['name']}")

    if artist_evo.get("new_discoveries"):
        summary.append(
            f"\n🆕 New Discoveries ({len(artist_evo['new_discoveries'])} artists):"
        )
        for artist in artist_evo["new_discoveries"][:5]:
            summary.append(f"  • {artist['name']}")

    # Genre evolution
    genre_evo = evolution_data.get("genre_evolution", {})
    if "short_term" in genre_evo:
        summary.append("\n🎵 Current Top Genres:")
        for genre_data in genre_evo["short_term"][:5]:
            summary.append(
                f"  • {genre_data['genre']} ({genre_data['percentage']:.1f}%)"
            )

    return "\n".join(summary)


if __name__ == "__main__":
    # Test historical analysis
    try:
        analyzer = HistoricalStatsAnalyzer()

        print("Analyzing listening evolution...")
        evolution = analyzer.analyze_listening_evolution()
        print(format_evolution_summary(evolution))

        print("\nAnalyzing discovery patterns...")
        discovery = analyzer.get_discovery_patterns()
        print(f"Discovery rate: {discovery.get('discovery_rate', 0):.1f}%")

        print("\nAnalyzing listening diversity...")
        diversity = analyzer.analyze_listening_diversity()

        print("\nAnalyzing mood patterns...")
        mood = analyzer.get_mood_analysis()

        # Export data
        all_analysis = {
            "evolution": evolution,
            "discovery": discovery,
            "diversity": diversity,
            "mood": mood,
        }

        export_historical_data(all_analysis, "data/historical_analysis.json")

    except Exception as e:
        print(f"Error: {e}")
