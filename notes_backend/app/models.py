from __future__ import annotations

import json
import os
import threading
import time
import uuid
from typing import Dict, List, Optional


class PersistenceError(Exception):
    """Raised when there is an error while persisting or loading notes."""


class _ThreadSafeJSONStore:
    """
    A minimal thread-safe JSON file store.
    Stores a list of note objects: [{id, title, content, created_at, updated_at}]
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._lock = threading.RLock()
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        # Initialize file if missing
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"notes": []}, f)

    def load(self) -> List[Dict]:
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("notes", [])
            except Exception as exc:
                raise PersistenceError(f"Failed to load notes: {exc}") from exc

    def save(self, notes: List[Dict]) -> None:
        with self._lock:
            try:
                tmp_path = f"{self.file_path}.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump({"notes": notes}, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, self.file_path)
            except Exception as exc:
                raise PersistenceError(f"Failed to save notes: {exc}") from exc


class NotesRepository:
    """
    Repository that manages Note objects with JSON file persistence.
    """

    def __init__(self, storage_file: Optional[str] = None):
        base_dir = storage_file or os.environ.get("NOTES_STORAGE_FILE")
        if not base_dir:
            # Default to local storage directory within container
            base_dir = os.path.join(os.path.dirname(__file__), "..", "storage", "notes.json")
        self._store = _ThreadSafeJSONStore(os.path.abspath(base_dir))
        self._cache = self._store.load()
        self._index: Dict[str, int] = {n["id"]: i for i, n in enumerate(self._cache)}

    def _now(self) -> float:
        return time.time()

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Dict]:
        """Return all notes ordered by created_at ascending."""
        return sorted(self._cache, key=lambda n: n.get("created_at", 0.0))

    # PUBLIC_INTERFACE
    def get_note(self, note_id: str) -> Optional[Dict]:
        """Return a note by id if it exists, else None."""
        idx = self._index.get(note_id)
        if idx is None:
            return None
        return self._cache[idx]

    # PUBLIC_INTERFACE
    def create_note(self, title: str, content: str) -> Dict:
        """Create and persist a new note."""
        new_note = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        self._cache.append(new_note)
        self._index[new_note["id"]] = len(self._cache) - 1
        self._store.save(self._cache)
        return new_note

    # PUBLIC_INTERFACE
    def update_note(self, note_id: str, title: Optional[str], content: Optional[str]) -> Optional[Dict]:
        """Update title/content for an existing note; returns updated note or None if not found."""
        idx = self._index.get(note_id)
        if idx is None:
            return None
        note = self._cache[idx]
        if title is not None:
            note["title"] = title
        if content is not None:
            note["content"] = content
        note["updated_at"] = self._now()
        self._cache[idx] = note
        self._store.save(self._cache)
        return note

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: str) -> bool:
        """Delete a note by id; returns True if deleted, False if not found."""
        idx = self._index.get(note_id)
        if idx is None:
            return False
        # Remove from cache and rebuild index for correctness
        del self._cache[idx]
        self._index = {n["id"]: i for i, n in enumerate(self._cache)}
        self._store.save(self._cache)
        return True


# Singleton repository instance for app usage
_repo_instance: Optional[NotesRepository] = None

# PUBLIC_INTERFACE
def get_repository() -> NotesRepository:
    """Return the singleton NotesRepository, initializing if necessary."""
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = NotesRepository()
    return _repo_instance
