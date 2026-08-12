"""What the language model is asked when a job needs a prompt nobody typed.

The video instruction is inherited knowledge, not code: collab-toolbox's prompt_converter notebook
does this same conversion, and its rules are what a Wan I2V prompt needs. Nothing is read from that
file at runtime -- the tools share knowledge, never imports. The sound instruction is ours: that
notebook asks the user for the audio prompt, so there was nothing to bring over.

The transport is services/xai/client.py; this file only decides what to say.
"""

# English, and it stays English: it is written for the model, not for a reader of the screen. Wan's
# own prompts are English too.
VIDEO_INSTRUCTION = """
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


# Written for MMAudio, which takes a short list of what should be heard.
AUDIO_INSTRUCTION = """
You write the audio prompt for MMAudio, which adds sound to a short silent video clip.

You are given the prompt the still image was generated from (the scene) and the prompt the motion
was generated from (what happens). Write what would be heard.

Follow these rules:

Name the sounds themselves, as a short comma-separated list — fabric rustling, distant traffic,
water lapping.
Stay with what the scene and the motion imply; invent no event that is not in them.
No music: the scene's own sounds are what is wanted, not a soundtrack.
No speech, no singing, no voice-over: the lips in the video would not match.
Keep it to one line, no more than about fifteen words.

Output only the audio prompt itself, as plain text. No list markers, no quotes, no explanations.
"""


class VideoPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts):
        """`prompts` is what the frame already says, layer by layer. A video is made from the photo,
        so that is the one this writer reads."""
        return self._client.complete(VIDEO_INSTRUCTION, prompts.get("photo", ""))


class AudioPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts):
        """Sound is made from the whole frame: the scene is in the photo's prompt and what happens
        is in the video's, so both go in one message, each under its own label."""
        said = [f"Scene: {prompts.get('photo', '')}"]
        video = prompts.get("video")
        if video:
            said.append(f"Motion: {video}")
        return self._client.complete(AUDIO_INSTRUCTION, "\n".join(said))
