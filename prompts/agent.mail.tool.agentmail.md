# AgentMail Tool

The `agentmail_tool` lets you interact with the AgentMail API.

## Actions
- `list_inboxes` – List available inboxes. Optional: `limit`.
- `create_inbox` – Create a new inbox. Optional: `email`, `username`, `domain`, `display_name`.
- `send_email` – Send an email. Requires `inbox_id` (or configured default), `to`, and at least one of `text` or `html`. Optional: `subject`, `labels`.
- `list_messages` – List messages in an inbox. Requires `inbox_id`. Optional: `limit`.
- `get_message` – Retrieve a single message by `message_id`.

## Example usage
```json
{
  "action": "send_email",
  "inbox_id": "my-inbox@example.com",
  "to": "recipient@example.com",
  "subject": "Hello",
  "text": "This is a test."
}
```
