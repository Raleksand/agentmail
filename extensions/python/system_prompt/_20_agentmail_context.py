"""Inject email handling context into system prompt for agentmail sessions."""

import os

from helpers.extension import Extension
from agent import LoopData

CTX_AGENTMAIL_SESSION = "_agentmail_session"


class AgentmailContextPrompt(Extension):

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs,
    ):
        if not self.agent:
            return

        if not self.agent.context.data.get(CTX_AGENTMAIL_SESSION):
            return

        sender = self.agent.context.data.get("_agentmail_sender", "unknown")
        subject = self.agent.context.data.get("_agentmail_subject", "")
        outbox = self.agent.context.data.get("_agentmail_outbox", "")

        prompt = (
            f"email session — user communicates via email\n"
            f"sender email: {sender}\n"
            f"original subject: {subject}\n"
            f"do NOT use agentmail_tool to send replies — the system auto-replies with your final response\n"
            f"use your available tools (web search, code execution, etc.) to give accurate complete answers\n"
            f"write the full reply text in your final response it will be sent back as email\n"
            f"focus on content do not include subject line or greeting boilerplate unless appropriate\n"
        )

        # Add outbox instructions if available
        if outbox and os.path.isdir(outbox):
            prompt += (
                f"\nATTACHMENT OUTBOX: {outbox}\n"
                f"If you want to include files as email attachments, save them to the outbox directory above.\n"
                f"Use code_execution_tool to write files there. Example:\n"
                f"  with open('{outbox}/filename.txt', 'w') as f: f.write(content)\n"
                f"Any files in the outbox when you finish will be automatically attached to the reply email.\n"
                f"For translations, always save the translated text as a .txt file in the outbox AND include a brief summary in your response text.\n"
                f"Name files descriptively (e.g. prevod_na_ruski.txt, translation_en.txt).\n"
            )

        system_prompt.append(prompt)
