from dataclasses import dataclass, field
from typing import Dict, List
import pandas as pd

from modules.data.base import BaseEntity
from modules.models.classifier import auto_tag


# Item Data

@dataclass
class ItemData(BaseEntity):
    """Represent a single item in a receipt."""

    name: str
    price: float
    category: str = "Others"

    def __init__(self, name: str, price: float, category: str = None):
        super().__init__(prefix="item")
        self.name = name.strip().title()
        self.price = float(price)
        self.category = category or auto_tag(self.name)

    def to_dict(self) -> dict:
        """Convert item to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "price": self.price,
            "category": self.category,
        })
        return base


#  Receipt Data

@dataclass
class ReceiptData(BaseEntity):
    """Structure for receipts parsed by AI or user-edited."""

    items: Dict[str, ItemData] = field(default_factory=dict)
    total: float = 0.0
    meta: dict = field(default_factory=dict)

    def __init__(self, items: Dict[str, ItemData], total: float):
        super().__init__(prefix="receipt")
        self.items = items
        self.total = float(total)
        self.meta = {}

    # Basic Computation

    @property
    def subtotal(self) -> float:
        """Sum of all item prices (pre-tax)."""
        return round(sum(it.price for it in self.items.values()), 2)

    def recalculate_total(self):
        """Recalculate total (auto-update after edits)."""
        self.total = self.subtotal
        return self.total

    # Editing Helpers

    def add_item(self, name: str, price: float, category: str = None):
        """Add new item safely."""
        idx = len(self.items) + 1
        item_id = f"item_{idx:03d}"
        self.items[item_id] = ItemData(name, price, category or auto_tag(name))
        self.recalculate_total()

    def update_from_dataframe(self, df: pd.DataFrame):
        """Update items from edited DataFrame (used by Streamlit editor)."""
        self.items.clear()
        for i, row in df.iterrows():
            self.add_item(
                name=str(row.get("name", "")).strip(),
                price=float(row.get("price", 0)),
                category=str(row.get("category", "Others")).strip()
            )
        self.recalculate_total()

    # Data Conversions

    def to_dataframe(self) -> pd.DataFrame:
        """Convert receipt to pandas DataFrame."""
        df = pd.DataFrame([i.to_dict() for i in self.items.values()])
        df["receipt_id"] = self.id
        return df[["name", "price", "category", "receipt_id"]]

    def to_dict(self) -> dict:
        """Convert receipt to dictionary (JSON-friendly)."""
        base = super().to_dict()
        base.update({
            "subtotal": self.subtotal,
            "total": self.total,
            "items": [i.to_dict() for i in self.items.values()],
        })
        return base

    @classmethod
    def from_list(cls, data: List[dict], total: float) -> "ReceiptData":
        """Build ReceiptData from list of {name, price, category}."""
        items = {
            f"item_{i:03d}": ItemData(
                d.get("name", ""),
                d.get("price", 0),
                d.get("category", "Others")
            )
            for i, d in enumerate(data)
        }
        return cls(items=items, total=total)

    # Analytics Helpers

    def get_most_expensive(self) -> ItemData:
        """Return the most expensive item."""
        return max(self.items.values(), key=lambda x: x.price)

    def get_category_summary(self) -> pd.DataFrame:
        """Summarize total spending by category."""
        df = self.to_dataframe()
        summary = (
            df.groupby("category")[["price"]]
            .sum()
            .sort_values("price", ascending=False)
            .reset_index()
        )
        summary.rename(columns={"price": "total_spent"}, inplace=True)
        return summary

    def get_percentage_breakdown(self) -> pd.DataFrame:
        """Get spending percentage per category."""
        summary = self.get_category_summary()
        total = summary["total_spent"].sum()
        summary["percentage"] = (summary["total_spent"] / total * 100).round(2)
        return summary