from dataclasses import dataclass
from typing import Dict, List
import random

from modules.data.assignment_data import SplitManager, GroupData, ParticipantData
from modules.data.receipt_data import ReceiptData

# Auto Split Engine

@dataclass
class AutoSplitEngine:
    """AI-assisted logic to auto-assign items to participants."""

    manager: SplitManager

    # Rule-Based Split Recommendation

    def run_auto_split(self) -> None:
        """Automatically assign items to participants (AI heuristic)."""
        participants = self.manager.get_all_participants()
        items = self.manager.get_all_items()

        if not participants:
            print("No participants found for auto split.")
            return

        # Heuristic: distribute items evenly by category or index
        category_map: Dict[str, List] = {}
        for item in items:
            category_map.setdefault(item.category, []).append(item)

        # Assign each category block to random participant
        for cat, cat_items in category_map.items():
            assigned_to = random.choice(participants)
            for it in cat_items:
                assigned_to.assign_item(it, ratio=1.0)
                print(f"Auto assigned {it.name} → {assigned_to.name}")

    # Equal Split (Optional)

    def run_equal_split(self) -> None:
        """Evenly split all items among all participants."""
        participants = self.manager.get_all_participants()
        items = self.manager.get_all_items()

        if not participants:
            return

        for item in items:
            ratio = 1 / len(participants)
            for p in participants:
                p.assign_item(item, ratio)
                print(f"{p.name} gets {ratio*100:.0f}% of {item.name}")

    # Save Back to Manager

    def update_manager(self) -> None:
        """Re-attach the group data to SplitManager."""
        self.manager.group_data = self.manager.group_data