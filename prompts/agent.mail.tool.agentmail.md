# AgentMail Tool

The `agentmail_tool` lets you interact with the AgentMail API.

## Actions
- `list_inboxes` – List available inboxes. Optional: `limit`.
- `create_inbox` – Create a new inbox. Optional: `email`, `username`, `domain`, `display_name`.
- `send_email` – Send an email. Requires `inbox_id` (or configured default), `to`, and at least one of `text`, `html`, or `attachments`. Optional: `subject`, `labels`, `thread_id`, `attachments`.
- `list_messages` – List messages in an inbox. Requires `inbox_id`. Optional: `limit`.
- `get_message` – Retrieve a single message by `message_id`.

## Attachments
The `attachments` parameter is a JSON array of objects. Each object must have:
- `content` (required): Base64-encoded file content (use `base64 -w0` to encode)
- `filename` (optional): The file name, e.g. `report.pdf`
- `content_type` (optional): MIME type, e.g. `text/plain`, `application/pdf`, `image/png`

Any file type is supported — PDF, images, documents, ZIP, audio, video, etc.

## Thread Support
Use `thread_id` with `send_email` to reply within an existing email thread. Get `thread_id` from `list_messages` results.

## Example usage

### Send plain email
```json
{
  "action": "send_email",
  "inbox_id": "my-inbox@example.com",
  "to": "recipient@example.com",
  "subject": "Hello",
  "text": "This is a test."
}
```

### Send email with TXT attachment
```json
{
  "action": "send_email",
  "inbox_id": "my-inbox@example.com",
  "to": "recipient@example.com",
  "subject": "Report attached",
  "text": "Please find the report attached.",
  "attachments": [
    {
      "content": "SGVsbG8gV29ybGQ=",
      "filename": "report.txt",
      "content_type": "text/plain"
    }
  ]
}
```

### Reply within a thread
```json
{
  "action": "send_email",
  "inbox_id": "my-inbox@example.com",
  "to": "sender@example.com",
  "subject": "Re: Question",
  "text": "Here is my reply.",
  "thread_id": "abc123-def456-..."
}
```
