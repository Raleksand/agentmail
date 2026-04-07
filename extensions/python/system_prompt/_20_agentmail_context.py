"""Inject email handling context into system prompt for agentmail sessions."""

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

        system_prompt.append(
            "email session user communicates via email\n"
            "response tool sends email dont use python\n"
            "use your available tools (web search, code execution, etc.) to give accurate complete answers\n"
            "write the full reply text in your final response it will be sent back as email\n"
            "focus on content do not include subject line or greeting boilerplate unless appropriate"
        )
