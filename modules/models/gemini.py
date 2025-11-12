import base64
import json
import os
from io import BytesIO
from PIL import Image

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from modules.data.receipt_data import ReceiptData, ItemData
from modules.utils import AIError, SettingsError
from modules.models.classifier import auto_tag
from modules.models.base import AIModel


MODEL_NAME = "gemini-2.5-flash"

PROMPT = """
You are an AI specialized in reading receipts.
The receipt contains item names and prices only.

Return valid JSON in this format:
{
  "menus": [{"name": "Latte", "price": 25000}, {"name": "Cake", "price": 20000}],
  "total": 45000
}
Rules:
- Remove currency symbols or commas.
- Return only JSON (no extra text).
"""


class GeminiModel(AIModel):
    """Simplified Gemini model with safe JSON parsing and fallback."""

    def __init__(self) -> None:
        key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not key:
            raise SettingsError("Missing GOOGLE_API_KEY")
        print("Initializing Gemini AI Model...")
        self.llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.0)
        self.model_name = "Gemini"

    def _encode_image(self, image: Image.Image) -> str:
        buf = BytesIO()
        image.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def run(self, image: Image.Image) -> ReceiptData:
        try:
            msg = HumanMessage(content=[
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": f"data:image/png;base64,{self._encode_image(image)}"}
            ])
            response = self.llm.invoke([msg]).content
            if not isinstance(response, str):
                raise AIError("Gemini returned non-text response")

            clean = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)

            menus = data.get("menus", [])
            total = float(data.get("total", 0))

            items = {
                f"item_{i}": ItemData(m["name"], float(m["price"]))
                for i, m in enumerate(menus) if "name" in m and "price" in m
            }
            print("Gemini parsing successful.")
            return ReceiptData(items=items, total=total)

        except Exception as e:
            print(f"Gemini failed: {e}")
            print("Fallback to Donut OCR model...")
            from modules.models.donut import DonutModel
            return DonutModel().run(image)