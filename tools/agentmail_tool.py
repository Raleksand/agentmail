import importlib
import json

from helpers import plugins
from helpers.tool import Tool, Response


class AgentmailTool(Tool):
    name = "agentmail_tool"
    description = "Send and receive emails via the AgentMail API."

    @staticmethod
    def _fmt(data):
        try:
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            return str(data)

    async def execute(self, action="", **kwargs):
        def arg(name, default=None):
            return kwargs.get(name, self.args.get(name, default))

        action = str(action or arg("action", "")).strip()

        try:
            config = plugins.get_plugin_config("agentmail", agent=self.agent) or {}
            client_mod = importlib.import_module("usr.plugins.agentmail.helpers.agentmail_client")
            client_mod = importlib.reload(client_mod)
            client = client_mod.AgentMailClient(config)

            if action == "list_inboxes":
                limit = int(arg("limit", 100))
                result = client.list_inboxes(limit=limit)
                return Response(message=self._fmt(result), break_loop=False)

            if action == "create_inbox":
                result = client.create_inbox(
                    email=arg("email"),
                    username=arg("username"),
                    domain=arg("domain"),
                    display_name=arg("display_name"),
                )
                return Response(message=self._fmt(result), break_loop=False)

            if action == "send_email":
                inbox_id = arg("inbox_id") or config.get("default_inbox")
                to = arg("to")
                subject = arg("subject", "")
                text = arg("text")
                html = arg("html")
                labels = arg("labels")
                attachments = arg("attachments")
                thread_id = arg("thread_id")

                if not inbox_id:
                    return Response(message="Error: Missing inbox_id", break_loop=False)
                if not to:
                    return Response(message="Error: Missing to", break_loop=False)
                if text is None and html is None and not attachments:
                    return Response(message="Error: Missing text, html, or attachments", break_loop=False)

                if isinstance(to, str):
                    to = [to]

                result = client.send_email(
                    inbox_id=inbox_id,
                    to=to,
                    subject=subject,
                    text=text,
                    html=html,
                    labels=labels,
                    attachments=attachments,
                    thread_id=thread_id,
                )
                return Response(message=self._fmt(result), break_loop=False)

            if action == "list_messages":
                inbox_id = arg("inbox_id") or config.get("default_inbox")
                limit = int(arg("limit", 100))
                if not inbox_id:
                    return Response(message="Error: Missing inbox_id", break_loop=False)
                result = client.list_messages(inbox_id=inbox_id, limit=limit)
                return Response(message=self._fmt(result), break_loop=False)

            if action == "get_message":
                message_id = arg("message_id")
                if not message_id:
                    return Response(message="Error: Missing message_id", break_loop=False)
                result = client.get_message(message_id)
                return Response(message=self._fmt(result), break_loop=False)

            return Response(message=f"Error: Unknown action: {action}", break_loop=False)
        except Exception as e:
            return Response(message=f"Error in agentmail_tool: {e}", break_loop=False)
