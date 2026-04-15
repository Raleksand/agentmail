# AgentMail Integration

AgentMail Integration is an Agent Zero plugin for sending and receiving email through the [AgentMail API](https://agentmail.to/), including attachments and thread support.

## Features

- **Send email** — plain text, HTML, or both
- **Attachments** — send any file type as a Base64-encoded attachment
- **Thread replies** — reply within an existing email thread using `thread_id`
- **List inboxes & messages** — browse available inboxes and read messages
- **Get message** — retrieve a single message by ID
- **Download attachments** — programmatically download and decode email attachments
- **Auto-reply (poller)** — process incoming emails automatically via a cron-based poller
- **Per-agent configuration** — each agent can use its own API key, base URL, and default inbox

## Plugin Files

| File | Purpose |
|------|----------|
| `plugin.yaml` | Plugin metadata |
| `tools/agentmail_tool.py` | Agent Zero tool implementation |
| `helpers/agentmail_client.py` | AgentMail API client (send, list, get, download attachments) |
| `api/process_email.py` | Loopback endpoint for email-to-agent processing |
| `extensions/python/system_prompt/_20_agentmail_context.py` | System prompt override for email sessions |
| `prompts/agent.system.tool.agentmail.md` | System-level tool documentation |
| `prompts/agent.mail.tool.agentmail.md` | Tool-level usage documentation |
| `webui/config.html` | Plugin configuration UI |
| `webui/agentmail-config-store.js` | Config store for the UI |
| `default_config.yaml` | Default configuration values |
| `execute.py` | Installs required runtime dependency (`requests`) |

## Configuration

Open **Settings → External → AgentMail Integration** and configure:

| Field | Description |
|-------|-------------|
| **API Base URL** | Usually `https://api.agentmail.to/v0` |
| **API Key** | Your AgentMail API key |
| **Default Inbox ID** | Inbox used when a tool call omits `inbox_id` |

## Tool Actions

| Action | Required args | Optional args |
|--------|---------------|---------------|
| `list_inboxes` | — | `limit` |
| `create_inbox` | — | `email`, `username`, `domain`, `display_name` |
| `send_email` | `inbox_id`, `to` | `subject`, `text`, `html`, `labels`, `attachments`, `thread_id` |
| `list_messages` | `inbox_id` | `limit` |
| `get_message` | `message_id` | — |

### Attachments

The `attachments` parameter is a JSON array of objects:

```json
{
  "content": "<base64-encoded file content>",
  "filename": "report.pdf",
  "content_type": "application/pdf"
}
```

- `content` is required — use `base64 -w0` to encode files
- `filename` and `content_type` are optional
- Any file type is supported: PDF, images, documents, ZIP, audio, video, etc.

### Thread Support

Use `thread_id` with `send_email` to reply within an existing email thread:

1. Get the `thread_id` from `list_messages` results
2. Pass it when calling `send_email`

## Auto-Reply with Poller

The plugin includes an internal loopback endpoint (`/api/plugins/agentmail/process_email`) that feeds incoming emails to Agent Zero for processing and returns the agent's reply. To automate this, you can set up a cron-based poller.

### Poller Setup

1. Place `agentmail_poll_once.py` in your work directory
2. Add a cron job to run it every minute:

```bash
crontab -e
# Add:
* * * * * /opt/venv/bin/python /a0/usr/workdir/agentmail_poll_once.py >> /a0/usr/workdir/poll.log 2>&1
```

The poller will:
- Check for new unread emails in the configured inbox
- Download and include text attachment content
- Send the email to Agent Zero for processing
- Automatically reply with the agent's response

### Safety Features

- File lock prevents concurrent runs
- Email IDs are recorded before processing (prevents re-processing on crash)
- Maximum emails per cycle (default: 5) prevents runaway processing

## Notes

- The plugin is intended to run inside Agent Zero
- The internal processing endpoint is for loopback use only (127.0.0.1)
- The poller script is deployment-specific and lives outside the plugin directory

## License

MIT
