from abc import ABC, abstractmethod
from PIL import Image
from modules.data.receipt_data import ReceiptData


class AIModel(ABC):
    """Abstract base class for all AI models."""

    @abstractmethod
    def run(self, image: Image.Image) -> ReceiptData:
        """Run the model to extract receipt data from an image."""
        pass

    def fallback(self, image: Image.Image) -> ReceiptData:
        """Fallback method if model fails."""
        raise NotImplementedError("No fallback model implemented.")