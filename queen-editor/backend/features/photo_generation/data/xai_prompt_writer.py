"""What the language model is asked when a job needs a prompt nobody typed.

The video instruction is inherited knowledge, not code: collab-toolbox's prompt_converter notebook
does this same conversion, and its rules are what a Wan I2V prompt needs. Nothing is read from that
file at runtime -- the tools share knowledge, never imports. The sound instruction is ours: that
notebook asks the user for the audio prompt, so there was nothing to bring over.

Two transports, one per model: H3's writer talks to Queen AI -- DeepSeek, services/deepseek/ -- and
shows it the frame's photo (madde 400); WAN's and the sound's talk to xAI, services/xai/. This file
only decides what to say.
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
# examples' (collab-toolbox's minimax-h3/workflow.json). Queen AI reads it with the frame's photo in
# front of it and the frame's scenario beside it (madde 400); Claude wrote the words on 2026-10-01
# and the user reads them afterwards (v8 roadmap). The line saying which picture sits where is not
# asked for: the producer writes it, because it is the graph's fact rather than the scene's. dynv2,
# the word that wakes the Motion Booster lora, is not asked for either: the user adds it by hand to
# the prompts that want it (madde 331), and the producer moves it in front (246).
H3_VIDEO_INSTRUCTION = """
You are an expert prompt writer for the MiniMax H3 video model.

Context
- H3 makes a video of four seconds, with sound, from a photo.
- The photo is the first frame of the video. H3 sees the photo too.
- The scenario says what happens in the video. Sometimes no scenario is given.
- The code writes the first line of the prompt. The line tells H3 where each photo sits in the video. Never write the line.

Work
- Look at the photo and read the scenario.
- Write the prompt in this form:

integrated_multimodal_description: [Shot 1] <the video>

overall_soundscape: <the sounds>

non_diegetic_music: N/A

Rules
- Write one shot. Never cut to a second shot.
- In the prompt, call the photo Picture 1.
- Start [Shot 1] with the style and the framing of Picture 1 in a few words, as in "3D CG, a medium shot of the man in Picture 1". Never describe Picture 1 again. H3 already sees Picture 1.
- Then write what moves and how, in order, from the first frame to the end of the video. Write only what fits in four seconds.
- Write the camera with the type, the amplitude and the speed, as in "The camera pushes in with small amplitude at slow speed." When the camera does not move, write "The camera holds a static shot."
- Use concrete words for what is seen and heard. Never use abstract words, as in beautiful or epic.
- If no scenario is given, write a small, natural motion for Picture 1.
- If the scenario has spoken words, give the speaker an ID and a short description of the voice, and put the spoken words inside <d> tags, as in: The young man with a warm voice (S1) says: <d>[English] Hello there.</d> Keep the spoken words exactly as in the scenario.
- If the scenario has no spoken words, write no speech at all, and end overall_soundscape with "No one speaks."
- In overall_soundscape, write one to four sentences about the sounds of the place, the movement and the breathing. Never repeat the spoken words there.
- Write only the prompt. No quotes, no explanations, no extra text.
"""


# What a loop video's prompt has to ask for, appended to whichever engine's instruction is being
# used (madde 307). One text for both, because loop is a mode of both engines.
#
# The clip is laid end to end several times, and its last frame IS its first. The model slows down
# to land on that frame and the next repeat starts from rest, which reads as a pulse every four
# seconds. A motion that returns arrives there by its own rhythm instead.
#
# Cutting the slowing frames off the end was the other way, and the user reasoned it out: it would
# take the last frame away from being the first, so the clip would stop looping at all.
#
# The same speed to the end (madde 315): most generators ease the subject toward stillness in the
# last frames, and asking for a cycle does not forbid that; H3's own loop advice asks for a constant
# speed too. Words can lessen the ease, not remove it -- the fix that does gives the seam a few
# frames of motion from both sides, and waits in the backlog.
#
# The camera holds still (madde 400): the last frame is the first photo again, so a camera that
# moved would have to travel back, and the return would show at the seam.
LOOP_RULE = """
This video is a loop. The last frame is the first photo again, and the video plays again and again.
- Write a motion that goes out and comes back to the first pose, as in swaying, breathing, a step that comes back, or hair that settles back.
- Keep the same speed from the first frame to the last. A motion that slows down or rests at the end shows as a stop each time the video starts again.
- The camera holds a static shot.
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

    def write(self, prompts, mode=production_mode.STANDARD, source=None, scene=""):
        """`prompts` is what the frame already says, layer by layer. A video is made from the photo,
        so that is the one this writer reads.

        `source` and `scene` are taken and ignored: grok is asked the photo's words alone, and the
        queue has one call shape for every writer.
        """
        return self._client.complete(asked(VIDEO_INSTRUCTION, mode), prompts.get("photo", ""))


class H3VideoPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts, mode=production_mode.STANDARD, source=None, scene=""):
        """Queen AI is shown the photo the video starts from and reads the frame's scenario
        (madde 400). The photo's own words are not sent: the model sees the picture they drew.

        A linked video is asked what a plain one is -- asked() adds words for a loop alone.
        """
        return self._client.complete(asked(H3_VIDEO_INSTRUCTION, mode),
                                     f"Scenario: {scene}" if scene else "", [source])


class AudioPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts, mode=production_mode.STANDARD, source=None, scene=""):
        """Sound is made from the whole frame: the scene is in the photo's prompt and what happens
        is in the video's, so both go in one message, each under its own label.

        `mode` is a video's business -- a sound is laid over the whole of one however it was made.
        It is taken and ignored, like `source` and `scene`, because the queue has one call shape for
        every writer.
        """
        said = [f"Scene: {prompts.get('photo', '')}"]
        video = prompts.get("video")
        if video:
            said.append(f"Motion: {video}")
        return self._client.complete(AUDIO_INSTRUCTION, "\n".join(said))
