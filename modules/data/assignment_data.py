from dataclasses import dataclass, field
from typing import Dict, List, Optional
from modules.data.receipt_data import ItemData
import uuid


# Participant Data


@dataclass
class ParticipantData:
    """Represent a participant involved in the bill split."""
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        self.name = self.name.strip().title()


# Assigned Item Data


@dataclass
class AssignedItemData:
    """Link a receipt item to a participant."""
    item: ItemData
    assigned_count: int = 1

    @property
    def total_price(self) -> float:
        return round(self.item.price * self.assigned_count, 2)


# Split Manager Core


class SplitManager:
    """Manage participants and their item assignments safely."""

    def __init__(self, participants: List[ParticipantData], receipt_items: Dict[str, ItemData]):
        self.participants: Dict[str, ParticipantData] = {p.id: p for p in participants}
        self.receipt_items: Dict[str, ItemData] = receipt_items
        self.participant_assignments: Dict[str, List[AssignedItemData]] = {}

        # Build quick lookup map for name → ItemData
        self.name_map: Dict[str, ItemData] = {
            item.name.lower(): item for item in self.receipt_items.values()
        }

    # Participant Management

    def add_participant(self, name: str):
        new_p = ParticipantData(name=name)
        self.participants[new_p.id] = new_p
        self.participant_assignments[new_p.id] = []

    def remove_participant(self, participant_id: str):
        self.participants.pop(participant_id, None)
        self.participant_assignments.pop(participant_id, None)

    # Assignment Logic

    def assign_item(self, participant_id: str, item_key: str, count: int = 1):
        """
        Assign item by either ID or Name (always safe).
        Never raises errors even if mismatched.
        """
        if participant_id not in self.participant_assignments:
            self.participant_assignments[participant_id] = []

        item = self._safe_lookup(item_key)

        if not item:
            # Skip silently instead of printing warnings
            return

        self.participant_assignments[participant_id].append(
            AssignedItemData(item=item, assigned_count=count)
        )

    def _safe_lookup(self, key: str) -> Optional[ItemData]:
        """
        Always find item safely by ID or name.
        Works even if item.id and dict key mismatch.
        """
        # Case 1: Match by dict key
        if key in self.receipt_items:
            return self.receipt_items[key]

        # Case 2: Match by exact name
        if key.lower() in self.name_map:
            return self.name_map[key.lower()]

        # Case 3: Match by partial fuzzy name
        for name, item in self.name_map.items():
            if key.lower() in name or name in key.lower():
                return item

        # Case 4: Match by item.id (fallback)
        for item in self.receipt_items.values():
            if getattr(item, "id", "") == key:
                return item

        # Nothing found
        return None

    def remove_assignment(self, participant_id: str, item_id: str):
        if participant_id not in self.participant_assignments:
            return
        self.participant_assignments[participant_id] = [
            it for it in self.participant_assignments[participant_id]
            if it.item.id != item_id
        ]

    # Retrieval & Calculation

    def get_assignments(self, participant_id: str) -> List[AssignedItemData]:
        return self.participant_assignments.get(participant_id, [])

    def get_total_assigned_for_item(self, item_id: str) -> int:
        total = 0
        for plist in self.participant_assignments.values():
            total += sum(a.assigned_count for a in plist if a.item.id == item_id)
        return total

    def get_participant_total(self, participant_id: str) -> float:
        assigns = self.participant_assignments.get(participant_id, [])
        return round(sum(a.total_price for a in assigns), 2)

    def get_summary(self) -> Dict[str, float]:
        return {
            p.name: self.get_participant_total(pid)
            for pid, p in self.participants.items()
        }

    def __repr__(self):
        return f"<SplitManager participants={len(self.participants)} items={len(self.receipt_items)}>"


# GroupData Wrapper

@dataclass
class GroupData:
    """Represent a split group session."""
    name: str = "Default Group"
    participants: List[ParticipantData] = field(default_factory=list)
    manager: Optional[SplitManager] = None

    def __post_init__(self):
        if self.manager is None:
            self.manager = SplitManager(self.participants, {})

    def add_participant(self, name: str):
        self.manager.add_participant(name)
        self.participants.append(ParticipantData(name=name))

    def get_summary(self) -> Dict[str, float]:
        return self.manager.get_summary()