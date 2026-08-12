"""What the language model is asked when a video job needs a prompt.

The instruction is inherited knowledge, not code: collab-toolbox's prompt_converter notebook does
this same conversion, and its rules are what a Wan I2V prompt needs. Nothing is read from that file
at runtime -- the tools share knowledge, never imports.

The transport is services/xai/client.py; this file only decides what to say.
"""

# English, and it stays English: it is written for the model, not for a reader of the screen. Wan's
# own prompts are English too.
INSTRUCTION = """
You are an expert prompt engineer specializing in image-to-video generation with the Wan model.
I will give you one SDXL prompt that was used to generate a still image. Convert it into an
optimized Wan image-to-video (I2V) positive prompt.

Follow these rules:

Don't re-describe the static scene in detail — Wan already receives the actual image as input. The
image defines the appearance; your job is to define motion.
Keep the camera static — no camera movement, no zoom, no pan.
Focus primarily on the action in the image — bring the subject's main activity to life as natural,
continuous movement. Build the motion around what the subject is actively doing.
Add subtle secondary motion to support the main action (hair, clothing, breathing, environmental
details like wind or water).
Keep it natural and physically plausible — realistic motion looks better than exaggerated movement
that breaks the image.
Specify pacing and mood.

Output only the motion prompt itself, as one concise paragraph of plain text. No list, no
surrounding quotes, no numbering, no explanations, no markdown code fences, no extra text.
"""


class VideoPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts):
        """`prompts` is what the frame already says, layer by layer. A video is made from the photo,
        so that is the one this writer reads."""
        return self._client.complete(INSTRUCTION, prompts.get("photo", ""))
