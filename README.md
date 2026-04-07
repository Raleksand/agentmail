# AgentMail Integration

AgentMail Integration is an Agent Zero plugin for sending and receiving email through the AgentMail API.

## Features

- Send email via AgentMail
- List inboxes and messages
- Read a single message by message ID
- Per-agent configuration for API URL, API key, and default inbox
- Internal loopback email-processing endpoint for local polling workflows

## Plugin Files

- `plugin.yaml` — plugin metadata
- `tools/agentmail_tool.py` — Agent Zero tool implementation
- `helpers/agentmail_client.py` — AgentMail API client
- `api/process_email.py` — loopback endpoint for email-to-agent processing
- `webui/config.html` — plugin configuration UI
- `webui/agentmail-config-store.js` — config store for the UI
- `default_config.yaml` — default configuration values
- `execute.py` — installs required runtime dependency

## Configuration

Open **Settings -> External -> AgentMail Integration** and configure:

- **API Base URL** — usually `https://api.agentmail.to/v0`
- **API Key** — your AgentMail API key
- **Default Inbox ID** — inbox address or inbox ID used by default

## Tool Actions

The plugin exposes these actions through the AgentMail tool:

- `list_inboxes`
- `create_inbox`
- `send_email`
- `list_messages`
- `get_message`

## Notes

- The plugin is intended to run inside Agent Zero.
- Email polling automation can be implemented separately, for example with cron calling a local poll script.
- The internal processing endpoint is intended for loopback use only.
