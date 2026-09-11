from app.agent.tools.audit_tools import save_audit_log
from app.agent.tools.calendar_tools import (
    create_event,
    delete_event,
    list_events,
    update_event,
)
from app.agent.tools.scheduling_tools import find_free_slots


ALL_TOOLS = [
    list_events,
    create_event,
    update_event,
    delete_event,
    find_free_slots,
    save_audit_log,
]


__all__ = ["ALL_TOOLS"]
