"""
Data storage and analysis module for persistent Spotify data management.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

Base = declarative_base()


class User(Base):
    """User table for storing Spotify user information."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    display_name = Column(String)
    email = Column(String)
    country = Column(String)
    followers = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Track(Base):
    """Track table for storing track information."""

    __tablename__ = "tracks"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    duration_ms = Column(Integer)
    popularity = Column(Integer)
    explicit = Column(Boolean)
    preview_url = Column(String)
    external_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Artist(Base):
    """Artist table for storing artist information."""

    __tablename__ = "artists"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    popularity = Column(Integer)
    followers = Column(Integer)
    external_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Album(Base):
    """Album table for storing album information."""

    __tablename__ = "albums"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    album_type = Column(String)
    release_date = Column(String)
    total_tracks = Column(Integer)
    external_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Genre(Base):
    """Genre table for storing genre information."""

    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ListeningHistory(Base):
    """Listening history table for tracking play events."""

    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    track_id = Column(String, ForeignKey("tracks.id"), nullable=False)
    played_at = Column(DateTime, nullable=False)
    progress_ms = Column(Integer)
    is_current = Column(Boolean, default=False)
    source = Column(String)  # 'recent', 'current', 'manual'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        Index("idx_user_played_at", "user_id", "played_at"),
        Index("idx_track_played_at", "track_id", "played_at"),
    )


class TopItem(Base):
    """Top items table for storing top tracks/artists over time."""

    __tablename__ = "top_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    item_id = Column(String, nullable=False)  # track_id or artist_id
    item_type = Column(String, nullable=False)  # 'track' or 'artist'
    time_range = Column(String, nullable=False)  # 'short_term', 'medium_term', 'long_term'
    rank = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_user_time_range", "user_id", "time_range", "recorded_at"),
        Index("idx_item_rank", "item_id", "rank"),
    )


class AudioFeatures(Base):
    """Audio features table for storing track audio characteristics."""

    __tablename__ = "audio_features"

    track_id = Column(String, ForeignKey("tracks.id"), primary_key=True)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Integer)
    loudness = Column(Float)
    mode = Column(Integer)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    time_signature = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisSnapshot(Base):
    """Analysis snapshots table for storing periodic analysis results."""

    __tablename__ = "analysis_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    analysis_type = Column(String, nullable=False)  # 'diversity', 'mood', 'evolution'
    analysis_data = Column(Text, nullable=False)  # JSON data
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_user_analysis_type", "user_id", "analysis_type", "created_at"),)


@dataclass
class DataStorageConfig:
    """Configuration for data storage."""

    database_url: str
    backup_dir: str = "data/backups"
    export_dir: str = "data/exports"
    enable_backups: bool = True
    backup_frequency_days: int = 7


class SpotifyDataManager:
    """Manages persistent storage and retrieval of Spotify data."""

    def __init__(self, config: Optional[DataStorageConfig] = None):
        """
        Initialize the data manager.

        Args:
            config: Data storage configuration.
        """
        if config is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/spoticron.db")
            config = DataStorageConfig(database_url=database_url)

        self.config = config
        self.engine = create_engine(config.database_url)
        self.session_factory = sessionmaker(bind=self.engine)

        # Create directories
        Path(config.backup_dir).mkdir(parents=True, exist_ok=True)
        Path(config.export_dir).mkdir(parents=True, exist_ok=True)

        # Create tables
        Base.metadata.create_all(self.engine)

    def store_user_info(self, user_data: Dict[str, Any]) -> bool:
        """
        Store or update user information.

        Args:
            user_data: User data from Spotify API.

        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.session_factory()

            user = session.query(User).filter_by(id=user_data["id"]).first()

            if user:
                # Update existing user (updated_at will be set automatically by onupdate)
                user.display_name = user_data.get("display_name") or user.display_name
                user.email = user_data.get("email") or user.email
                user.country = user_data.get("country") or user.country
                user.followers = user_data.get("followers", {}).get("total", 0)
            else:
                # Create new user
                user = User(
                    id=user_data["id"],
                    display_name=user_data.get("display_name"),
                    email=user_data.get("email"),
                    country=user_data.get("country"),
                    followers=user_data.get("followers", {}).get("total", 0),
                )
                session.add(user)

            session.commit()
            session.close()
            return True

        except Exception as e:
            print(f"Error storing user info: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def store_track(self, track_data: Dict[str, Any]) -> bool:
        """
        Store track information.

        Args:
            track_data: Track data from Spotify API.

        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.session_factory()

            # Check if track already exists
            existing_track = session.query(Track).filter_by(id=track_data["id"]).first()

            if not existing_track:
                track = Track(
                    id=track_data["id"],
                    name=track_data["name"],
                    duration_ms=track_data.get("duration_ms"),
                    popularity=track_data.get("popularity"),
                    explicit=track_data.get("explicit", False),
                    preview_url=track_data.get("preview_url"),
                    external_url=track_data.get("external_urls", {}).get("spotify"),
                )
                session.add(track)
                session.commit()

            session.close()
            return True

        except Exception as e:
            print(f"Error storing track: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def store_listening_history(self, user_id: str, listening_data: List[Dict[str, Any]]) -> bool:
        """
        Store listening history data.

        Args:
            user_id: Spotify user ID.
            listening_data: List of listening events.

        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.session_factory()

            for item in listening_data:
                # Parse played_at timestamp
                if isinstance(item.get("played_at"), str):
                    played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
                else:
                    played_at = item.get("played_at", datetime.utcnow())

                # Check if this exact listening event already exists
                existing = (
                    session.query(ListeningHistory)
                    .filter_by(
                        user_id=user_id,
                        track_id=item.get("track_id"),
                        played_at=played_at,
                    )
                    .first()
                )

                if not existing:
                    history_entry = ListeningHistory(
                        user_id=user_id,
                        track_id=item.get("track_id"),
                        played_at=played_at,
                        progress_ms=item.get("progress_ms"),
                        is_current=item.get("is_current", False),
                        source=item.get("source", "recent"),
                    )
                    session.add(history_entry)

            session.commit()
            session.close()
            return True

        except Exception as e:
            print(f"Error storing listening history: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def store_top_items(self, user_id: str, top_data: Dict[str, Any]) -> bool:
        """
        Store top tracks/artists data.

        Args:
            user_id: Spotify user ID.
            top_data: Top items data with time ranges.

        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.session_factory()
            recorded_at = datetime.utcnow()

            for time_range, data in top_data.get("time_ranges", {}).items():
                if not data:
                    continue

                # Store top tracks
                for track in data.get("tracks", []):
                    top_item = TopItem(
                        user_id=user_id,
                        item_id=track["track_id"],
                        item_type="track",
                        time_range=time_range,
                        rank=track["rank"],
                        recorded_at=recorded_at,
                    )
                    session.add(top_item)

                # Store top artists
                for artist in data.get("artists", []):
                    top_item = TopItem(
                        user_id=user_id,
                        item_id=artist["artist_id"],
                        item_type="artist",
                        time_range=time_range,
                        rank=artist["rank"],
                        recorded_at=recorded_at,
                    )
                    session.add(top_item)

            session.commit()
            session.close()
            return True

        except Exception as e:
            print(f"Error storing top items: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def store_audio_features(self, features_data: List[Dict[str, Any]]) -> bool:
        """
        Store audio features for tracks.

        Args:
            features_data: List of audio features from Spotify API.

        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.session_factory()

            for features in features_data:
                if not features or not features.get("id"):
                    continue

                # Check if features already exist
                existing = session.query(AudioFeatures).filter_by(track_id=features["id"]).first()

                if not existing:
                    audio_features = AudioFeatures(
                        track_id=features["id"],
                        danceability=features.get("danceability"),
                        energy=features.get("energy"),
                        key=features.get("key"),
                        loudness=features.get("loudness"),
                        mode=features.get("mode"),
                        speechiness=features.get("speechiness"),
                        acousticness=features.get("acousticness"),
                        instrumentalness=features.get("instrumentalness"),
                        liveness=features.get("liveness"),
                        valence=features.get("valence"),
                        tempo=features.get("tempo"),
                        time_signature=features.get("time_signature"),
                    )
                    session.add(audio_features)

            session.commit()
            session.close()
            return True

        except Exception as e:
            print(f"Error storing audio features: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False

    def get_listening_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get listening statistics for a user over a period.

        Args:
            user_id: Spotify user ID.
            days: Number of days to analyze.

        Returns:
            Dictionary with listening statistics.
        """
        try:
            session = self.session_factory()

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Get listening history
            history = (
                session.query(ListeningHistory)
                .filter(
                    ListeningHistory.user_id == user_id,
                    ListeningHistory.played_at >= start_date,
                    ListeningHistory.played_at <= end_date,
                )
                .all()
            )

            # Calculate statistics
            total_plays = len(history)
            unique_tracks = len(set(h.track_id for h in history))

            # Get track information for played tracks
            track_ids = [h.track_id for h in history]
            tracks = session.query(Track).filter(Track.id.in_(track_ids)).all()
            track_dict = {t.id: t for t in tracks}

            # Calculate total listening time
            total_duration_ms = sum(track_dict[h.track_id].duration_ms for h in history if h.track_id in track_dict)

            listening_stats = {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_plays": total_plays,
                "unique_tracks": unique_tracks,
                "total_listening_time_hours": total_duration_ms / (1000 * 60 * 60),
                "average_plays_per_day": total_plays / days if days > 0 else 0,
                "average_listening_hours_per_day": (total_duration_ms / (1000 * 60 * 60)) / days if days > 0 else 0,
            }

            session.close()
            return listening_stats

        except Exception as e:
            print(f"Error getting listening stats: {e}")
            if "session" in locals():
                session.close()
            return {}

    def export_user_data(self, user_id: str, export_format: str = "json") -> Optional[str]:
        """
        Export all user data to a file.

        Args:
            user_id: Spotify user ID.
            export_format: Export format ('json' or 'csv').

        Returns:
            Path to exported file or None if failed.
        """
        try:
            session = self.session_factory()

            # Get all user data
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return None

            # Get listening history
            history = session.query(ListeningHistory).filter_by(user_id=user_id).all()

            # Get top items
            top_items = session.query(TopItem).filter_by(user_id=user_id).all()

            # Prepare export data
            export_data = {
                "user_info": {
                    "id": user.id,
                    "display_name": user.display_name,
                    "email": user.email,
                    "country": user.country,
                    "followers": user.followers,
                },
                "listening_history": [
                    {
                        "track_id": h.track_id,
                        "played_at": h.played_at.isoformat(),
                        "progress_ms": h.progress_ms,
                        "source": h.source,
                    }
                    for h in history
                ],
                "top_items": [
                    {
                        "item_id": t.item_id,
                        "item_type": t.item_type,
                        "time_range": t.time_range,
                        "rank": t.rank,
                        "recorded_at": t.recorded_at.isoformat(),
                    }
                    for t in top_items
                ],
                "export_timestamp": datetime.utcnow().isoformat(),
            }

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spotify_data_{user_id}_{timestamp}.{export_format}"
            filepath = Path(self.config.export_dir) / filename

            # Export data
            if export_format.lower() == "json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                # For CSV, would need pandas implementation
                print("CSV export not yet implemented")
                return None

            session.close()
            return str(filepath)

        except Exception as e:
            print(f"Error exporting user data: {e}")
            if "session" in locals():
                session.close()
            return None

    def create_backup(self) -> Optional[str]:
        """
        Create a backup of the database.

        Returns:
            Path to backup file or None if failed.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"spoticron_backup_{timestamp}.db"
            backup_path = Path(self.config.backup_dir) / backup_filename

            # For SQLite databases, we can just copy the file
            if self.config.database_url.startswith("sqlite:"):
                db_path = self.config.database_url.replace("sqlite:///", "")
                if Path(db_path).exists():
                    import shutil

                    shutil.copy2(db_path, backup_path)
                    return str(backup_path)

            return None

        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """
        Clean up old data beyond the specified retention period.

        Args:
            days_to_keep: Number of days of data to retain.

        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.session_factory()
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            # Delete old listening history
            old_history = session.query(ListeningHistory).filter(ListeningHistory.created_at < cutoff_date).delete()

            # Delete old analysis snapshots
            old_snapshots = session.query(AnalysisSnapshot).filter(AnalysisSnapshot.created_at < cutoff_date).delete()

            session.commit()
            session.close()

            print(f"Cleaned up {old_history} old listening records and {old_snapshots} old snapshots")
            return True

        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            if "session" in locals():
                session.rollback()
                session.close()
            return False


def get_data_manager() -> SpotifyDataManager:
    """
    Get a configured data manager instance.

    Returns:
        SpotifyDataManager instance.
    """
    return SpotifyDataManager()


if __name__ == "__main__":
    # Test data manager
    manager = get_data_manager()

    # Test user storage
    test_user = {
        "id": "test_user_123",
        "display_name": "Test User",
        "email": "test@example.com",
        "country": "US",
        "followers": {"total": 10},
    }

    success = manager.store_user_info(test_user)
    print(f"User storage test: {'✓' if success else '✗'}")

    # Test statistics
    stats = manager.get_listening_stats("test_user_123", 30)
    print(f"Stats retrieval test: {'✓' if stats else '✗'}")

    # Test backup
    backup_path = manager.create_backup()
    print(f"Backup test: {'✓' if backup_path else '✗'}")

    print("Data manager tests completed.")
