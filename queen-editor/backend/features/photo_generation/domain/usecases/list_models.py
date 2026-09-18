"""Which rows the Model box and the LoRA box offer.

A row is `{"value", "label"}`: what the renderer is sent, and what the user reads. The value is an
id from the catalog and the label is the name it is picked by.

The models are the ones the notebook installed, in the order it lists them. With none, photo was
not installed on this machine, and the answer is an empty list rather than a question to ComfyUI:
asking it for checkpoints there could only come back empty or fall over, and falling over put an
error card on the project screen (madde 229).
"""
from backend.features.photo_generation.domain import catalog

# The lora box's first row. No value: it is not a lora but the model's own arrangement.
STANDARD = {"value": "", "label": "Standart"}


def list_models(chosen):
    # An id this checkout does not know is a notebook that moved ahead of it. Dropping the one row
    # keeps the rest usable; emptying the list would close the panel for a reason the user cannot
    # act on.
    found = [catalog.find_model(model_id) for model_id in chosen]
    return [{"value": model["id"], "label": model["label"]} for model in found if model]


def list_loras():
    """Standart, then every lora. Not filtered by the notebook: the lora files come down with the
    photo group whatever was ticked, so every one of them is on any machine that renders photos."""
    return [STANDARD] + [{"value": lora["id"], "label": lora["label"]} for lora in catalog.LORAS]
