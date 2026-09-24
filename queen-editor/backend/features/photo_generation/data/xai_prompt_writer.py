"""What the language model is asked when a job needs a prompt nobody typed.

The video instruction is inherited knowledge, not code: collab-toolbox's prompt_converter notebook
does this same conversion, and its rules are what a Wan I2V prompt needs. Nothing is read from that
file at runtime -- the tools share knowledge, never imports. The sound instruction is ours: that
notebook asks the user for the audio prompt, so there was nothing to bring over.

The transport is services/xai/client.py; this file only decides what to say.
"""
from backend.features.photo_generation.domain import production_mode

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


# Written for MiniMax H3 (madde 243), whose prompt is sectioned and whose sound comes out of the same
# pass as the picture -- so the soundscape is this writer's too. The sections are the graph's own
# examples' (collab-toolbox's minimax-h3/workflow.json). The sentence saying which picture sits where
# is not asked for: the producer writes it, because it is the graph's fact rather than the scene's.
# dynv2, the word that wakes the Motion Booster lora, is not asked for either: the user adds it by
# hand to the prompts that want it (madde 331), and the producer moves it in front (246).
H3_VIDEO_INSTRUCTION = """
You are a prompt writer for the MiniMax H3 video model.

I give you: the SDXL prompt of a photo. This photo is the first frame of the video.

I want: the H3 prompt for that video.

Write it like this:

integrated_multimodal_description: [Shot 1] <the motion>

overall_soundscape: <the sounds>

non_diegetic_music: N/A

Rules:
- The motion: do not describe the photo again, the model already sees it. Say what moves and how. The camera does not move. Keep it natural.
- The sounds: only what the scene and the motion would make.
- Write only the prompt. No quotes, no explanations, no extra text.
"""


# What a loop video's prompt has to ask for, appended to whichever engine's instruction is being
# used (madde 307). One sentence for both, because loop is a mode of both engines.
#
# The clip is laid end to end several times, and its last frame IS its first. The model slows down
# to land on that frame and the next repeat starts from rest, which reads as a pulse every four
# seconds. A motion that returns arrives there by its own rhythm instead.
#
# Cutting the slowing frames off the end was the other way, and the user reasoned it out: it would
# take the last frame away from being the first, so the clip would stop looping at all.
#
# The last sentence asks for one speed to the end (madde 315). Most generators ease the subject
# toward stillness in the last frames, and asking for a cycle does not forbid that; H3's own loop
# advice asks for a constant speed too. Words can lessen the ease, not remove it -- the fix that does
# gives the seam a few frames of motion from both sides, and waits in the backlog.
LOOP_RULE = """
This clip loops: it is played several times back to back, and its last frame is its first frame.
Write a motion that returns to where it started -- a cycle, not a movement that ends. Swaying,
breathing, a step that comes back, hair that settles where it was.
It must be a motion that does not end: one that finishes and comes to rest reads as a stop every
time the clip repeats.
Keep the same speed from the first frame to the last: the motion must not slow down toward the end.
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


def asked(instruction, mode):
    """The engine's own instruction, plus what this mode adds to it.

    Appended rather than woven in: a plain video is asked exactly what it was asked before, and one
    test holds that.
    """
    return instruction + LOOP_RULE if mode == production_mode.LOOP else instruction


class VideoPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts, mode=production_mode.STANDARD):
        """`prompts` is what the frame already says, layer by layer. A video is made from the photo,
        so that is the one this writer reads."""
        return self._client.complete(asked(VIDEO_INSTRUCTION, mode), prompts.get("photo", ""))


class H3VideoPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts, mode=production_mode.STANDARD):
        """Made from the photo, like WAN's: the video starts from that picture."""
        return self._client.complete(asked(H3_VIDEO_INSTRUCTION, mode), prompts.get("photo", ""))


class AudioPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts, mode=production_mode.STANDARD):
        """Sound is made from the whole frame: the scene is in the photo's prompt and what happens
        is in the video's, so both go in one message, each under its own label.

        `mode` is a video's business -- a sound is laid over the whole of one however it was made.
        Taken and ignored, because the queue has one call shape for every writer.
        """
        said = [f"Scene: {prompts.get('photo', '')}"]
        video = prompts.get("video")
        if video:
            said.append(f"Motion: {video}")
        return self._client.complete(AUDIO_INSTRUCTION, "\n".join(said))
