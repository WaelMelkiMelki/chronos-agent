from __future__ import annotations

from typing import Any
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel

from app.db.session import get_session_factory
from app.models.audit_log import AuditLog


class SaveAuditLogInput(BaseModel):
    action_type: str
    entity_type: str
    entity_id: str | None = None
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    executed_by: str = "agent"


@tool("save_audit_log", args_schema=SaveAuditLogInput)
async def save_audit_log(
    action_type: str, entity_type: str, entity_id: str | None = None,
    old_value: dict[str, Any] | None = None, new_value: dict[str, Any] | None = None,
    executed_by: str = "agent", config: RunnableConfig | None = None,
) -> dict[str, Any]:
    cfg = config or {}
    user_id = UUID(str(cfg.get("configurable", {}).get("user_id")))
    factory = get_session_factory()
    async with factory() as db:
        log = AuditLog(user_id=user_id, action_type=action_type, entity_type=entity_type, entity_id=entity_id, old_value=old_value, new_value=new_value, executed_by=executed_by)
        db.add(log)
        await db.commit()
        return {"audit_id": str(log.id)}
