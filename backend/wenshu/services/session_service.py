
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# In a production environment, consider using a more robust cache like Redis
# to handle scalability, persistence, and automatic expiration.
_sessions: Dict[str, Dict[str, Any]] = {}

class SessionService:
    """
    A singleton service to manage user sessions for multi-step interactions in memory.
    """

    def create_session(self, user_id: str = "default_user") -> str:
        """
        Creates a new session with a unique ID and basic metadata.

        Args:
            user_id: An identifier for the user initiating the session.

        Returns:
            The unique session ID for the newly created session.
        """
        session_id = str(uuid.uuid4())
        _sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "document_state": None,  # Will hold the in-memory docx object
            "history": [],  # To track the conversation and actions
        }
        print(f"✅ Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a session by its ID.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            The session data dictionary, or None if not found.
        """
        return _sessions.get(session_id)

    def update_session(self, session_id: str, key: str, value: Any) -> bool:
        """
        Updates a specific key within a session.

        Args:
            session_id: The ID of the session to update.
            key: The key of the data to update within the session.
            value: The new value to set.

        Returns:
            True if the update was successful, False otherwise.
        """
        if session_id in _sessions:
            _sessions[session_id][key] = value
            _sessions[session_id]["last_updated"] = datetime.utcnow()
            print(f"🔄 Session updated: {session_id}, Key: {key}")
            return True
        print(f"❌ Session not found for update: {session_id}")
        return False

    def add_history(self, session_id: str, event: Dict[str, Any]) -> bool:
        """
        Adds a new event to the session's history log.

        Args:
            session_id: The ID of the session.
            event: A dictionary describing the event (e.g., user feedback, AI action).

        Returns:
            True if successful, False otherwise.
        """
        if session_id in _sessions:
            event_with_timestamp = {**event, "timestamp": datetime.utcnow().isoformat()}
            _sessions[session_id]["history"].append(event_with_timestamp)
            self.update_session(session_id, "last_updated", datetime.utcnow())
            return True
        return False

    def end_session(self, session_id: str) -> bool:
        """
        Removes a session from memory.

        Args:
            session_id: The ID of the session to end.

        Returns:
            True if the session was found and removed, False otherwise.
        """
        if session_id in _sessions:
            del _sessions[session_id]
            print(f"🗑️ Session ended: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self, expiry_minutes: int = 60):
        """
        Removes sessions that have not been updated for a specified duration.
        """
        now = datetime.utcnow()
        expired_ids = [
            sid
            for sid, sdata in _sessions.items()
            if now - sdata.get("last_updated", now) > timedelta(minutes=expiry_minutes)
        ]
        for sid in expired_ids:
            self.end_session(sid)
        if expired_ids:
            print(f"🧹 Cleaned up {len(expired_ids)} expired sessions.")

# Create a single instance of the service to be used across the application
session_service = SessionService()
