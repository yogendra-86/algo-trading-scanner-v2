import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class SessionStore:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

        if not self.file_path.exists():
            self._write({})

    def _read(self) -> Dict[str, Any]:
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _write(self, data: Dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get(self, chat_id: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            data = self._read()
            return data.get(str(chat_id))

    def set(self, chat_id: int, value: Dict[str, Any]) -> None:
        with self._lock:
            data = self._read()
            data[str(chat_id)] = value
            self._write(data)

    def clear(self, chat_id: int) -> None:
        with self._lock:
            data = self._read()
            data.pop(str(chat_id), None)
            self._write(data)
