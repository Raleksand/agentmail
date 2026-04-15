import os
from urllib.parse import quote

import requests


class AgentMailClient:
    def __init__(self, config: dict | None = None):
        config = config or {}
        self.base_url = str(config.get("api_base_url", "https://api.agentmail.to/v0")).rstrip("/")
        self.api_key = config.get("api_key") or os.getenv("AGENTMAIL_API_KEY")
        if not self.api_key:
            raise ValueError("AgentMail API key not provided")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", 30)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        if not response.text:
            return {}
        return response.json()

    def list_inboxes(self, limit: int = 100):
        return self._request("GET", f"/inboxes?limit={int(limit)}")

    def create_inbox(
        self,
        email: str | None = None,
        username: str | None = None,
        domain: str | None = None,
        display_name: str | None = None,
    ):
        payload = {}
        if email:
            payload["email"] = email
        if username:
            payload["username"] = username
        if domain:
            payload["domain"] = domain
        if display_name:
            payload["display_name"] = display_name
        return self._request("POST", "/inboxes", json=payload)

    def send_email(
        self,
        inbox_id,
        to,
        subject: str = "",
        text: str | None = None,
        html: str | None = None,
        labels: list | None = None,
        attachments: list | None = None,
        thread_id: str | None = None,
    ):
        payload = {
            "to": to,
            "subject": subject,
            "text": text,
            "html": html,
            "labels": labels or [],
            "attachments": attachments or [],
            "thread_id": thread_id,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        return self._request("POST", f"/inboxes/{inbox_id}/messages/send", json=payload)

    def list_messages(self, inbox_id, limit: int = 100):
        return self._request("GET", f"/inboxes/{inbox_id}/messages?limit={int(limit)}")

    def get_message(self, message_id):
        clean_id = str(message_id).strip().strip("<>").strip()
        return self._request("GET", f"/messages/{quote(clean_id, safe='@._-')}")

    # ── Attachment handling ──────────────────────────────────────────────

    _TEXT_EXTENSIONS = frozenset(
        ".txt .md .csv .json .xml .html .log .py .js .css .yaml .yml .ini .cfg .sh .bat".split()
    )

    def download_attachment(self, inbox_id: str, thread_id: str, attachment_id: str) -> bytes | None:
        """Download an attachment's raw content via the thread endpoint.

        Returns the file bytes, or None on failure.
        """
        try:
            meta = self._request(
                "GET",
                f"/inboxes/{inbox_id}/threads/{thread_id}/attachments/{attachment_id}",
            )
            download_url = meta.get("download_url")
            if not download_url:
                return None
            resp = self.session.get(download_url, timeout=30)
            resp.raise_for_status()
            return resp.content
        except Exception:
            return None

    def get_attachment_text(
        self,
        inbox_id: str,
        thread_id: str,
        attachments: list[dict],
    ) -> str:
        """Download text attachments and return their combined content.

        Binary attachments are noted by filename and size only.
        """
        parts: list[str] = []
        for att in attachments:
            filename = att.get("filename", "unknown")
            content_type = att.get("content_type", "")
            att_id = att.get("attachment_id", "")
            if not att_id:
                continue

            content = self.download_attachment(inbox_id, thread_id, att_id)
            if content is None:
                parts.append(f"[Attachment: {filename} — download failed]")
                continue

            is_text = (
                content_type.startswith("text/")
                or any(filename.lower().endswith(ext) for ext in self._TEXT_EXTENSIONS)
            )

            if is_text:
                try:
                    text = content.decode("utf-8")
                    parts.append(
                        f"--- Attachment: {filename} ---\n{text}\n--- End of attachment ---"
                    )
                except UnicodeDecodeError:
                    parts.append(
                        f"[Attachment: {filename} ({len(content)} bytes, binary content)]"
                    )
            else:
                parts.append(
                    f"[Attachment: {filename} ({content_type}, {len(content)} bytes)]"
                )

        return "\n\n".join(parts)
