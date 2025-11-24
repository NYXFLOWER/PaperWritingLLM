"""Session Management and Logging"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml


class SessionManager:
    """Manage user sessions and conversation logging"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize session manager"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.session_config = self.config['session']
        self.ui_config = self.config['ui']
        self.log_directory = self.session_config['log_directory']
        self.username = None
        self.session_id = None
        self.session_start = None
        self.conversation_history = []
        self.user_dir = None
        self.log_file = None

    def start_session(self, username: str, custom_instructions: Optional[str] = None) -> str:
        """Start a new session for a user"""
        self.username = username
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")

        # Create user directory if it doesn't exist
        self.user_dir = Path(self.log_directory) / username
        self.user_dir.mkdir(parents=True, exist_ok=True)

        # Create session log file
        log_filename = f"session_{self.session_id}.jsonl"
        self.log_file = self.user_dir / log_filename

        # Initialize conversation history
        self.conversation_history = []

        # Log session start
        self._write_log_entry({
            "type": "session_start",
            "timestamp": self.session_start.isoformat(),
            "username": username,
            "session_id": self.session_id,
            "custom_instructions": custom_instructions
        })

        return str(self.log_file)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        if self.session_id is None:
            raise RuntimeError("No active session. Call start_session() first.")

        timestamp = datetime.now()
        message = {
            "role": role,
            "content": content
        }

        # Add to in-memory history
        self.conversation_history.append(message)

        # Log to file
        self._write_log_entry({
            "type": "message",
            "timestamp": timestamp.isoformat(),
            "role": role,
            "content": content
        })

        # Trim history if needed
        max_history = self.session_config.get('max_history', 50)
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.conversation_history.copy()

    def end_session(self) -> None:
        """End the current session"""
        if self.session_id is None:
            return

        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds()

        # Log session end
        self._write_log_entry({
            "type": "session_end",
            "timestamp": session_end.isoformat(),
            "duration_seconds": duration,
            "messages_count": len(self.conversation_history)
        })

        # Create summary file
        self._create_session_summary()

        # Reset session
        self.session_id = None
        self.conversation_history = []

    def _write_log_entry(self, entry: Dict[str, Any]) -> None:
        """Write a log entry to the session file"""
        if self.log_file is None:
            return

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def _create_session_summary(self) -> None:
        """Create a human-readable summary of the session"""
        if self.log_file is None:
            return

        summary_file = self.log_file.with_suffix('.txt')

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Writing Assistant Session Summary\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Username: {self.username}\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Start Time: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Messages: {len(self.conversation_history)}\n")
            f.write(f"\n" + "=" * 50 + "\n\n")

            # Write conversation
            for msg in self.conversation_history:
                role = msg['role'].upper()
                content = msg['content']
                f.write(f"{role}:\n{content}\n\n")
                f.write("-" * 50 + "\n\n")

    def list_user_sessions(self, username: str) -> List[str]:
        """List all sessions for a user"""
        user_dir = Path(self.log_directory) / username
        if not user_dir.exists():
            return []

        sessions = []
        for log_file in user_dir.glob("session_*.jsonl"):
            sessions.append(log_file.stem)

        return sorted(sessions, reverse=True)

    def load_session_history(self, username: str, session_id: str) -> List[Dict[str, Any]]:
        """Load conversation history from a previous session"""
        user_dir = Path(self.log_directory) / username
        log_file = user_dir / f"session_{session_id}.jsonl"

        if not log_file.exists():
            raise FileNotFoundError(f"Session file not found: {log_file}")

        messages = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get('type') == 'message':
                    messages.append({
                        'role': entry['role'],
                        'content': entry['content'],
                        'timestamp': entry['timestamp']
                    })

        return messages
