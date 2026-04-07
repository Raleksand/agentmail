### agentmail_tool
Send and receive emails via the AgentMail API.

**Actions:**
- `list_inboxes` — List available inboxes. Optional: `limit`
- `create_inbox` — Create a new inbox. Optional: `email`, `username`, `domain`, `display_name`
- `send_email` — Send an email. Requires `inbox_id` (or configured default), `to`, and at least one of `text` or `html`. Optional: `subject`, `labels`
- `list_messages` — List messages in an inbox. Requires `inbox_id`. Optional: `limit`
- `get_message` — Retrieve a single message by `message_id`

**Usage examples:**

1. Send email:
~~~json
{
    "tool_name": "agentmail_tool",
    "tool_args": {
        "action": "send_email",
        "inbox_id": "your-inbox@agentmail.to",
        "to": "recipient@example.com",
        "subject": "Hello from AgentMail",
        "text": "This is the plain text body."
    }
}
~~~

2. Create inbox:
~~~json
{
    "tool_name": "agentmail_tool",
    "tool_args": {
        "action": "create_inbox",
        "username": "support",
        "domain": "agentmail.to",
        "display_name": "Support Inbox"
    }
}
~~~

3. List messages:
~~~json
{
    "tool_name": "agentmail_tool",
    "tool_args": {
        "action": "list_messages",
        "inbox_id": "your-inbox@agentmail.to",
        "limit": "10"
    }
}
~~~

4. Get single message:
~~~json
{
    "tool_name": "agentmail_tool",
    "tool_args": {
        "action": "get_message",
        "message_id": "msg_abc123"
    }
}
~~~
