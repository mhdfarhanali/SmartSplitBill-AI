from enum import Enum
from modules.models.base import AIModel


class ModelNames(str, Enum):
    GEMINI = "Gemini"
    DONUT = "Donut"


def get_model_instance(model_name: ModelNames) -> AIModel:
    """Return a model instance based on selected model name."""
    if model_name == ModelNames.GEMINI:
        try:
            from modules.models.gemini import GeminiModel
            return GeminiModel()
        except Exception as err:
            print(f"Gemini model failed: {err}. Falling back to Donut...")
            from modules.models.donut import DonutModel
            return DonutModel()

    elif model_name == ModelNames.DONUT:
        from modules.models.donut import DonutModel
        return DonutModel()

    raise ValueError(f"Unknown model: {model_name}")