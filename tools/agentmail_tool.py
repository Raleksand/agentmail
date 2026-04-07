from helpers.tool import Tool, Response
from usr.plugins.agentmail.helpers.agentmail_client import AgentMailClient


class AgentmailTool(Tool):
    name = "agentmail_tool"
    description = "Send and receive emails via the AgentMail API."

    async def execute(self, args):
        action = str(args.get("action", "")).strip()
        config = self.get_plugin_config() or {}
        client = AgentMailClient(config)

        if action == "list_inboxes":
            limit = int(args.get("limit", 100))
            result = client.list_inboxes(limit=limit)
            return Response(success=True, data=result)

        if action == "create_inbox":
            email = args.get("email")
            username = args.get("username")
            domain = args.get("domain")
            display_name = args.get("display_name")
            result = client.create_inbox(
                email=email,
                username=username,
                domain=domain,
                display_name=display_name,
            )
            return Response(success=True, data=result)

        if action == "send_email":
            inbox_id = args.get("inbox_id") or config.get("default_inbox")
            to = args.get("to")
            subject = args.get("subject", "")
            text = args.get("text")
            html = args.get("html")
            labels = args.get("labels")

            if not inbox_id:
                return Response(success=False, error="Missing inbox_id")
            if not to:
                return Response(success=False, error="Missing to")
            if text is None and html is None:
                return Response(success=False, error="Missing text or html")

            if isinstance(to, str):
                to = [to]

            result = client.send_email(
                inbox_id=inbox_id,
                to=to,
                subject=subject,
                text=text,
                html=html,
                labels=labels,
            )
            return Response(success=True, data=result)

        if action == "list_messages":
            inbox_id = args.get("inbox_id") or config.get("default_inbox")
            limit = int(args.get("limit", 100))
            if not inbox_id:
                return Response(success=False, error="Missing inbox_id")
            result = client.list_messages(inbox_id=inbox_id, limit=limit)
            return Response(success=True, data=result)

        if action == "get_message":
            message_id = args.get("message_id")
            if not message_id:
                return Response(success=False, error="Missing message_id")
            result = client.get_message(message_id)
            return Response(success=True, data=result)

        return Response(success=False, error=f"Unknown action: {action}")
