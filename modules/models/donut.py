from PIL import Image
import pytesseract
import re
from modules.data.receipt_data import ReceiptData, ItemData


class DonutModel:
    """Simple OCR-based fallback model (works offline)."""

    def __init__(self):
        print("Using Donut Fallback Model (OCR only)")

    def run(self, image: Image.Image) -> ReceiptData:
        text = pytesseract.image_to_string(image)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        items = {}

        # Extract format: name + price (last number)
        for i, line in enumerate(lines):
            match = re.findall(r"(.*?)(\d+[,.]?\d*)$", line)
            if match:
                name, price = match[0]
                try:
                    price_val = float(price.replace(",", "").replace(".", ""))
                    items[f"item_{i}"] = ItemData(name.strip(), price_val)
                except ValueError:
                    continue

        total = sum(it.price for it in items.values())
        return ReceiptData(items=items, total=total)