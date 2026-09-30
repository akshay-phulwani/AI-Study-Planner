from typing import Dict, Any, List
from src.database import get_full_roadmap_tree, get_roadmap_summary, get_active_profile


def get_formatted_roadmap_data() -> Dict[str, Any]:
    profile = get_active_profile()
    summary = get_roadmap_summary()
    tree = get_full_roadmap_tree()
    return {
        "profile": profile,
        "summary": summary,
        "phases": tree
    }
