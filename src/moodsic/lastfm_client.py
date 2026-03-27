import os
import pylast
import random
from typing import Any, List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class LastFMClient:
    """Wrapper for Last.fm API to fetch songs by genre/tags with variety"""
    
    def __init__(self):
        self.api_key = os.getenv("LASTFM_API_KEY", "").strip()
        self.api_secret = os.getenv("LASTFM_SHARED_SECRET", "").strip()
        
        if not self.api_key:
            raise ValueError("LASTFM_API_KEY not found in .env file")
        
        self.network = pylast.LastFMNetwork(
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        
        # Keep track of recently recommended songs to avoid repeats
        self.recently_recommended = []  # Store song IDs
        self.recent_limit = 20  # Don't repeat songs from last 20 recommendations

    def _get_title(self, track: Any) -> Optional[str]:
        getter = getattr(track, "get_title", None)
        if callable(getter):
            title = getter()
            return str(title) if title else None
        return None

    def _get_artist_name(self, track: Any) -> Optional[str]:
        artist_getter = getattr(track, "get_artist", None)
        if not callable(artist_getter):
            return None
        artist = artist_getter()
        if artist is None:
            return None
        name_getter = getattr(artist, "get_name", None)
        if callable(name_getter):
            artist_name = name_getter()
            return str(artist_name) if artist_name else None
        return None

    def _get_url(self, track: Any) -> Optional[str]:
        getter = getattr(track, "get_url", None)
        if callable(getter):
            url = getter()
            return str(url) if url else None
        return None

    def _normalize_image_list(self, value: Any) -> List[str]:
        if isinstance(value, (list, tuple)):
            return [str(item) for item in value if item]
        return []
    
    def get_tracks_by_tag(self, tag: str, limit: int = 5) -> List[Dict]:
        """Get top tracks for a given genre/tag with variety"""
        try:
            tag_obj = self.network.get_tag(tag)
            
            # Get more tracks than needed so we can randomize
            fetch_limit = limit * 3  # Fetch 3x more than needed
            top_tracks = tag_obj.get_top_tracks(limit=fetch_limit)
            
            tracks = []
            for top_item in top_tracks:
                track = getattr(top_item, "item", None)
                if track is None:
                    continue
                title = self._get_title(track)
                artist_name = self._get_artist_name(track)
                if not title or not artist_name:
                    continue
                
                # Skip if recently recommended
                track_id = f"{title}_{artist_name}".replace(" ", "_")
                if track_id in self.recently_recommended:
                    continue
                
                # Try to get album art
                album_art = self._get_track_art(track)
                url = self._get_url(track)
                
                tracks.append({
                    "id": track_id,
                    "title": title,
                    "artist": artist_name,
                    "url": url,
                    "genres": [tag],
                    "source": "lastfm",
                    "image_url": album_art
                })
            
            # Shuffle for variety
            random.shuffle(tracks)
            
            # Update recently recommended list
            for track in tracks[:limit]:
                self.recently_recommended.append(track["id"])
            
            # Keep recent list manageable
            self.recently_recommended = self.recently_recommended[-self.recent_limit:]
            
            return tracks[:limit]
            
        except Exception as e:
            print(f"Last.fm error for tag '{tag}': {e}")
            return []
    
    def get_tracks_by_multiple_tags(self, tags: List[str], limit_per_tag: int = 2) -> List[Dict]:
        """Get tracks for multiple genres/tags with variety and cross-tag deduplication"""
        all_tracks = []
        seen_ids = set()
        
        # Shuffle tags for variety
        shuffled_tags = tags.copy()
        random.shuffle(shuffled_tags)
        
        for tag in shuffled_tags:
            tracks = self.get_tracks_by_tag(tag, limit=limit_per_tag)
            
            for track in tracks:
                track_id = track["id"]
                if track_id not in seen_ids:
                    seen_ids.add(track_id)
                    all_tracks.append(track)
        
        # Shuffle final results
        random.shuffle(all_tracks)
        
        return all_tracks
    
    def _get_track_art(self, track: Any) -> Optional[str]:
        """Extract album art URL from track object"""
        try:
            # Try to get album info
            get_album = getattr(track, "get_album", None)
            if not callable(get_album):
                return None
            album = get_album()
            if album:
                # Try different methods to get cover image
                get_cover_image = getattr(album, "get_cover_image", None)
                if callable(get_cover_image):
                    cover = get_cover_image()
                    if cover:
                        return str(cover)
                
                get_cover_image_sizes = getattr(album, "get_cover_image_sizes", None)
                if callable(get_cover_image_sizes):
                    images = self._normalize_image_list(get_cover_image_sizes())
                    if images:
                        # Last image is usually largest
                        return images[-1]
            
            return None
        except Exception as e:
            # Silently fail - album art is optional
            return None
    
    def get_track_details(self, artist: str, title: str) -> Optional[Dict]:
        """Get detailed track info including album art"""
        try:
            track = self.network.get_track(artist, title)
            get_album = getattr(track, "get_album", None)
            album = get_album() if callable(get_album) else None
            
            images: List[str] = []
            if album:
                get_cover_image_sizes = getattr(album, "get_cover_image_sizes", None)
                if callable(get_cover_image_sizes):
                    images = self._normalize_image_list(get_cover_image_sizes())

            resolved_title = self._get_title(track) or title
            resolved_artist = self._get_artist_name(track) or artist
            resolved_url = self._get_url(track)
            
            return {
                "id": f"{title}_{artist}".replace(" ", "_"),
                "title": resolved_title,
                "artist": resolved_artist,
                "url": resolved_url,
                "image_url": images[-1] if images else None,
                "images": images
            }
        except Exception as e:
            print(f"Error getting track details: {e}")
            return None
    
    def search_tracks(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for tracks by name"""
        try:
            search_results = self.network.search_for_track(artist_name="", track_name=query)
            results = search_results.get_next_page()
            
            tracks = []
            for track in results[:limit]:
                title = self._get_title(track)
                artist_name = self._get_artist_name(track)
                if not title or not artist_name:
                    continue
                album_art = self._get_track_art(track)
                tracks.append({
                    "id": f"{title}_{artist_name}".replace(" ", "_"),
                    "title": title,
                    "artist": artist_name,
                    "url": self._get_url(track),
                    "image_url": album_art,
                    "genres": [],
                    "source": "lastfm"
                })
            
            return tracks
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    def get_similar_tracks(self, artist: str, track: str, limit: int = 5) -> List[Dict]:
        """Get tracks similar to a given track"""
        try:
            track_obj = self.network.get_track(artist, track)
            similar = track_obj.get_similar(limit=limit)
            
            tracks = []
            for similar_track in similar:
                similar_item = getattr(similar_track, "item", similar_track)
                title = self._get_title(similar_item)
                artist_name = self._get_artist_name(similar_item)
                if not title or not artist_name:
                    continue
                album_art = self._get_track_art(similar_item)
                tracks.append({
                    "id": f"{title}_{artist_name}".replace(" ", "_"),
                    "title": title,
                    "artist": artist_name,
                    "url": self._get_url(similar_item),
                    "image_url": album_art,
                    "match": getattr(similar_track, 'match', None)
                })
            
            return tracks
        except Exception as e:
            print(f"Error getting similar tracks: {e}")
            return []
    
    def clear_recent_history(self):
        """Clear the recent recommendations history to get fresh tracks"""
        self.recently_recommended = []
        print("Cleared recent recommendation history")

# Create a singleton instance
lastfm_client = LastFMClient()