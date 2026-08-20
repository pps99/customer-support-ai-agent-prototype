import json
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import ESCALATIONS_FILE


_escalations_lock = threading.Lock()


def create_escalation(
    reason: str,
    message: str,
    order_id: str | None = None,
    data_file: Path | None = None,
) -> dict[str, Any]:
    """Create and durably store a ticket queued for human review."""
    path = data_file or ESCALATIONS_FILE
    ticket_id = "ESC-" + str(uuid.uuid4())[:8]
    ticket = {
        "ticket_id": ticket_id,
        "status": "queued",
        "reason": reason,
        "order_id": order_id,
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with _escalations_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            with path.open(encoding="utf-8") as file:
                tickets = json.load(file)
        else:
            tickets = []

        tickets.append(ticket)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            json.dump(tickets, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_path = Path(temporary_file.name)

        os.replace(temporary_path, path)

    return ticket
