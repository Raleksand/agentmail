import os
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
    ):
        payload = {
            "inbox_id": inbox_id,
            "to": to,
            "subject": subject,
            "text": text,
            "html": html,
            "labels": labels or [],
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        return self._request("POST", "/messages/send", json=payload)

    def list_messages(self, inbox_id, limit: int = 100):
        return self._request("GET", f"/messages?inbox_id={inbox_id}&limit={int(limit)}")

    def get_message(self, message_id):
        return self._request("GET", f"/messages/{message_id}")
