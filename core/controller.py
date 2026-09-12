from config.settings import Settings
from sebi.core.brain import SEBIBrain
from sebi.core.models import ProcessRequest


class SEBIController(SEBIBrain):
    """Compatibility wrapper around the new SEBIBrain implementation."""

    def __init__(self, config: Settings) -> None:
        super().__init__(config)

    async def process_request(
        self,
        user_message: str,
        user_id: str | None = None,
        reasoning_effort: str = "medium",
    ):
        return self.process(
            ProcessRequest(
                message=user_message,
                user_id=user_id,
                output_format="markdown",
                remember=False,
            )
        )
