"""Which rows the Model box and the LoRA box offer.

A row is `{"value", "label"}`: what the renderer is sent, and what the user reads. The value is an
id from the catalog and the label is the name it is picked by. A model drawn with a lora box of its
own carries that box under "loras", Boş last, and one that takes no negative says
`"negative": False` (madde 486, 499): the panel shows that box in place of the shared one and hides
the negative, without knowing any model by its id. A row may carry a box and take a negative; a row
that carries neither leaves the shared boxes as its answer, as they always were.

The models are the ones the notebook installed, in the order it lists them. With none, photo was
not installed on this machine, and the answer is an empty list rather than a question to ComfyUI:
asking it for checkpoints there could only come back empty or fall over, and falling over put an
error card on the project screen (madde 229).
"""
from backend.features.photo_generation.domain import catalog

# Every lora box's last row: no lora at all.
NONE = {"value": catalog.NO_LORA, "label": "Boş"}


def list_models(chosen):
    # An id this checkout does not know is a notebook that moved ahead of it. Dropping the one row
    # keeps the rest usable; emptying the list would close the panel for a reason the user cannot
    # act on.
    found = [catalog.find_model(model_id) for model_id in chosen]
    return [_row(model) for model in found if model]


def _row(model):
    row = {"value": model["id"], "label": model["label"]}
    if "loras" in model:
        row["loras"] = _box(model["loras"])
    if "negative" in model:
        row["negative"] = model["negative"]
    return row


def list_loras():
    """Every lora, the default first, then Boş. Not filtered by the notebook: the lora files come
    down with the photo group whatever was ticked, so every one of them is on any machine that
    renders photos."""
    return _box(catalog.LORAS)


def _box(loras):
    return [{"value": lora["id"], "label": lora["label"]} for lora in loras] + [NONE]
