from __future__ import annotations


from typing import Any


from langchain_core.tools import tool
from pydantic import BaseModel




class SaveAuditLogInput(BaseModel):
    action_type: str
    entity_type: str
    entity_id: str | None = None
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    executed_by: str = "agent"




@tool("save_audit_log", args_schema=SaveAuditLogInput)
async def save_audit_log(**kwargs) -> dict:  # type: ignore[no-untyped-def]
    """Persist an audit log entry (auto-invoked by execute node)."""
    raise NotImplementedError("Wired to AuditService in Phase 4")
