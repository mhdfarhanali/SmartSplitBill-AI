from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

from modules.data.assignment_data import (
    AssignedItemData,
    ParticipantData,
    SplitManager,
)
from modules.utils import format_currency


# Purchased Item Report (Per Item)

@dataclass
class PurchasedItemReportData:
    """Represent a single purchased item by a participant."""
    name: str
    unit_price: float
    quantity: int
    total_price: float

    @classmethod
    def from_assignment(cls, assigned: AssignedItemData) -> "PurchasedItemReportData":
        """Convert from AssignedItemData → PurchasedItemReportData."""
        return cls(
            name=assigned.item.name,
            unit_price=assigned.item.price,
            quantity=assigned.assigned_count,
            total_price=assigned.total_price,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame or JSON."""
        return {
            "Item": self.name,
            "Unit Price": self.unit_price,
            "Qty": self.quantity,
            "Total": self.total_price,
        }


# Participant Report (Per Orang)

@dataclass
class ParticipantReportData:
    """Report for one participant (summary of assigned items)."""
    name: str
    items: List[PurchasedItemReportData]
    subtotal: float

    @classmethod
    def from_manager(cls, participant_id: str, manager: SplitManager) -> "ParticipantReportData":
        """Generate report for one participant from SplitManager."""
        participant = manager.participants.get(participant_id)
        if not participant:
            return cls(name="Unknown", items=[], subtotal=0.0)

        assignments = manager.get_assignments(participant_id)
        item_reports = [PurchasedItemReportData.from_assignment(a) for a in assignments]
        subtotal = round(sum(a.total_price for a in assignments), 2)

        return cls(name=participant.name, items=item_reports, subtotal=subtotal)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert this participant's report to a DataFrame."""
        df = pd.DataFrame([i.to_dict() for i in self.items])
        if not df.empty:
            df["Total"] = df["Total"].apply(format_currency)
            df["Unit Price"] = df["Unit Price"].apply(format_currency)
        return df

    def to_dict(self) -> dict:
        """Convert to dict for JSON or Streamlit use."""
        return {
            "name": self.name,
            "items": [i.to_dict() for i in self.items],
            "subtotal": self.subtotal,
        }


# Full Report (Gabungan Semua Peserta)


@dataclass
class ReportData:
    """Full spending report for all participants."""
    participants: List[ParticipantReportData]

    @classmethod
    def from_split_manager(cls, manager: SplitManager) -> "ReportData":
        """Generate full report from SplitManager."""
        all_reports = [
            ParticipantReportData.from_manager(pid, manager)
            for pid in manager.participants.keys()
        ]
        return cls(participants=all_reports)

    # Summary Table
 
    def to_summary_dataframe(self) -> pd.DataFrame:
        """Return a summary DataFrame of total spending per participant."""
        summary = [
            {"Participant": p.name, "Total Paid": p.subtotal}
            for p in self.participants
        ]
        df = pd.DataFrame(summary)
        if not df.empty:
            df["Total Paid"] = df["Total Paid"].apply(format_currency)
        return df

    # Total Keseluruhan

    def grand_total(self) -> float:
        """Return grand total of all participants."""
        return round(sum(p.subtotal for p in self.participants), 2)

    def to_dict(self) -> dict:
        """Convert full report into a dictionary."""
        return {
            "participants": [p.to_dict() for p in self.participants],
            "grand_total": self.grand_total(),
        }