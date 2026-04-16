import json
import os
import traceback
from helpers.api import ApiHandler, Input, Output, Request, Response
from helpers import guids
from agent import AgentContext, UserMessage
from initialize import initialize_agent
from helpers.defer import DeferredTask

# ── Thread mapping ──────────────────────────────────────────────────────────
THREADS_FILE = "/a0/usr/workdir/agentmail_threads.json"
OUTBOX_DIR = "/a0/usr/workdir/agentmail_outbox"


def _load_threads() -> dict:
    """Load thread_id → context_id mapping from disk."""
    try:
        if os.path.exists(THREADS_FILE):
            with open(THREADS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_threads(threads: dict):
    """Persist thread_id → context_id mapping to disk."""
    try:
        with open(THREADS_FILE, "w") as f:
            json.dump(threads, f, indent=2)
    except Exception:
        pass


def _get_or_create_context_id(thread_id: str | None, use_context_fn) -> str:
    """Return existing context_id for thread, or generate a new one and save mapping."""
    if not thread_id:
        # No thread — always a fresh context
        return str(guids.generate_id())

    threads = _load_threads()
    existing = threads.get(thread_id)
    if existing:
        # Verify the context still exists in memory
        ctx = AgentContext.get(existing)
        if ctx is not None:
            return existing
        # Context was lost (server restart?) — create new, keep mapping

    context_id = str(guids.generate_id())
    threads[thread_id] = context_id
    _save_threads(threads)
    return context_id


class ProcessEmail(ApiHandler):
    """Internal loopback-only endpoint: receives an email, hands it off to an
    AgentZero context (reusing existing context for the same thread), and
    returns the reply along with any outbox attachments.

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
            sender   = input.get("from", "unknown")
            subject  = input.get("subject", "(no subject)")
            body     = input.get("body", "").strip()
            thread_id = input.get("thread_id", "") or None

            if not body:
                return {"ok": False, "error": "Empty email body"}

            # Resolve or create context for this thread
            context_id = _get_or_create_context_id(thread_id, self.use_context)
            context = self.use_context(context_id)

            # Mark as agentmail session
            context.data["_agentmail_session"] = True
            context.data["_agentmail_sender"] = sender
            context.data["_agentmail_subject"] = subject

            # Set per-thread outbox so agent can save attachment files
            outbox_path = os.path.join(OUTBOX_DIR, context_id)
            os.makedirs(outbox_path, exist_ok=True)
            context.data["_agentmail_outbox"] = outbox_path

            msg = UserMessage(message=body, attachments=[])
            task = context.communicate(msg)
            result = await task.result()

            # Collect any files the agent saved to the outbox
            attachments = []
            if os.path.isdir(outbox_path):
                for fname in sorted(os.listdir(outbox_path)):
                    fpath = os.path.join(outbox_path, fname)
                    if os.path.isfile(fpath):
                        try:
                            with open(fpath, "rb") as f:
                                import base64
                                content_b64 = base64.b64encode(f.read()).decode("ascii")
                            # Guess MIME type
                            import mimetypes
                            mime_type, _ = mimetypes.guess_type(fpath)
                            if not mime_type:
                                mime_type = "application/octet-stream"
                            attachments.append({
                                "content": content_b64,
                                "filename": fname,
                                "content_type": mime_type,
                            })
                        except Exception:
                            pass

            return {
                "ok":          True,
                "response":    result or "",
                "context":     context_id,
                "thread_id":   thread_id or "",
                "attachments": attachments,
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
