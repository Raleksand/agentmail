import traceback
from helpers.api import ApiHandler, Input, Output, Request, Response
from helpers import guids
from agent import AgentContext, UserMessage
from initialize import initialize_agent
from helpers.defer import DeferredTask


class ProcessEmail(ApiHandler):
    """Internal loopback-only endpoint: receives an email, hands it off to a
    fresh AgentZero context, and returns the reply.
    Only reachable from 127.0.0.1 (loopback).
    """

    @classmethod
    def requires_auth(cls) -> bool:
        return False

    @classmethod
    def requires_csrf(cls) -> bool:
        return False

    @classmethod
    def requires_loopback(cls) -> bool:
        return True

    async def process(self, input: Input, request: Request) -> Output:
        try:
            sender  = input.get("from", "unknown")
            subject = input.get("subject", "(no subject)")
            body    = input.get("body", "").strip()

            if not body:
                return {"ok": False, "error": "Empty email body"}

            message_text = body

            context_id = str(guids.generate_id())
            context = self.use_context(context_id)
            context.data["_agentmail_session"] = True
            context.data["_agentmail_sender"] = sender
            context.data["_agentmail_subject"] = subject

            msg = UserMessage(message=message_text, attachments=[])
            task = context.communicate(msg)
            result = await task.result()

            return {
                "ok":       True,
                "response": result or "",
                "context":  context_id,
            }

        except Exception as e:
            tb = traceback.format_exc()
            try:
                with open("/a0/usr/workdir/process_email_error.log", "a") as f:
                    f.write(f"\n\n{'='*60}\n{tb}\n")
            except Exception:
                pass
            return {
                "ok":    False,
                "error": "Failed to process email",
            }
