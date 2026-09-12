from __future__ import annotations

from sebi.core.models import RequestContext, VerificationReport


class Verifier:
    """Applies sanity checks before SEBI returns a result."""

    def verify(self, context: RequestContext) -> VerificationReport:
        issues = []
        checks = {
            "has_intent": bool(context.intent),
            "has_tasks": len(context.tasks) > 0,
            "response_not_empty": bool(context.response_text.strip()),
            "knowledge_loaded": len(context.knowledge_items),
        }

        if not checks["has_intent"]:
            issues.append("Intent detection failed.")
        if not checks["has_tasks"]:
            issues.append("No task plan was created.")
        if not checks["response_not_empty"]:
            issues.append("The response is empty.")

        return VerificationReport(
            passed=not issues,
            checks=checks,
            issues=issues,
        )
