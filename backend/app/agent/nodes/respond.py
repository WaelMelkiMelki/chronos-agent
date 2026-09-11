"""Node: produce the final natural-language response."""

from __future__ import annotations
from typing import Any
from app.agent.state import AgentState


def _format_results(results: list[dict[str, Any]], language: str = "fr") -> str:
    if not results: return "Aucune action exécutée."
    lines: list[str] = []
    for r in results:
        status = r.get("status")
        tool = r.get("tool", "action")
        if status == "ok":
            if tool == "create_event": lines.append(f"✅ Événement créé : {r['output'].get('summary', '')}")
            elif tool == "delete_event": lines.append("🗑️ Événement supprimé")
            elif tool == "update_event": lines.append("✏️ Événement mis à jour")
            elif tool == "find_free_slots":
                slots = r.get("output", [])
                if slots:
                    lines.append(f"🕐 {len(slots)} créneau(x) disponible(s):")
                    for s in slots[:5]: lines.append(f"   • {s['start']} → {s['end']}")
                else: lines.append("❌ Aucun créneau trouvé")
            elif tool == "list_events":
                evs = r.get("output", [])
                lines.append(f"📅 {len(evs)} événement(s):")
                for e in evs[:10]: lines.append(f"   • {e['summary']} — {e['start']}")
            else: lines.append(f"✅ {tool}")
        elif status == "cancelled_by_user": lines.append("🚫 Action annulée")
        elif status == "not_found": lines.append(f"❓ Aucun événement ne correspond à « {r.get('query')} »")
        else: lines.append(f"⚠️ {tool}: {r.get('error', status)}")
    return "\n".join(lines)


async def respond(state: AgentState) -> AgentState:
    results = state.get("tool_results", [])
    state["final_response"] = _format_results(results, state.get("language", "fr"))
    return state
