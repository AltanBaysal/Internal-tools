from backend.features.photo_generation.data.xai_prompt_writer import (
    AUDIO_INSTRUCTION,
    VIDEO_INSTRUCTION,
    AudioPromptWriter,
    VideoPromptWriter,
)


class FakeClient:
    def __init__(self, answer="she turns her head"):
        self.answer = answer
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        return self.answer


def test_the_photo_prompt_is_what_the_model_is_asked_to_convert():
    client = FakeClient()

    written = VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"})

    assert written == "she turns her head"
    assert client.calls == [(VIDEO_INSTRUCTION, "kırmızı elbiseli kadın")]


def test_the_instruction_says_what_wan_needs_and_what_to_leave_out():
    # The rules are the whole value of this file: a drifted instruction is a wrong prompt.
    assert "image-to-video" in VIDEO_INSTRUCTION
    assert "Keep the camera static" in VIDEO_INSTRUCTION
    assert "Output only the motion prompt itself" in VIDEO_INSTRUCTION


def test_the_sound_is_written_from_both_prompts():
    client = FakeClient(answer="fabric rustling, footsteps on stone")

    written = AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın",
                                              "video": "kadın başını çeviriyor"})

    assert written == "fabric rustling, footsteps on stone"
    instruction, said = client.calls[0]
    assert instruction == AUDIO_INSTRUCTION
    # Both, labelled: the model has to know which is the scene and which is the motion.
    assert said.index("kırmızı elbiseli kadın") < said.index("kadın başını çeviriyor")


def test_a_frame_with_no_video_prompt_still_sends_what_it_has():
    client = FakeClient()

    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"})

    assert "kırmızı elbiseli kadın" in client.calls[0][1]


def test_the_sound_instruction_asks_for_the_scenes_own_sounds():
    assert "No music" in AUDIO_INSTRUCTION
    assert "No speech" in AUDIO_INSTRUCTION


def _h3():
    """Imported where it is used: a name that is not there yet would fail collection and take the
    WAN and sound questions above down with it."""
    from backend.features.photo_generation.data import xai_prompt_writer
    return xai_prompt_writer.H3_VIDEO_INSTRUCTION, xai_prompt_writer.H3VideoPromptWriter


def test_the_h3_writer_converts_the_photo_prompt_with_its_own_instruction():
    instruction, writer = _h3()
    client = FakeClient(answer="integrated_multimodal_description: dynv2. she turns")

    written = writer(client).write({"photo": "kırmızı elbiseli kadın"})

    assert written == "integrated_multimodal_description: dynv2. she turns"
    assert client.calls == [(instruction, "kırmızı elbiseli kadın")]


def test_the_h3_instruction_says_the_photo_is_the_first_frame():
    # The user's words (madde 246): the model is told plainly what the photo is to the video.
    instruction, _writer = _h3()

    assert "This photo is the first frame of the video." in instruction


def test_the_h3_instruction_opens_with_dynv2_unless_the_scene_is_calm():
    """The trigger is the writer's line rather than the code's (user's call, madde 243): it stays
    visible in the prompt box. Whether it is written is the scene's call, leaning to yes (madde 246);
    the producer then puts it first, so it no longer sits inside the section."""
    instruction, _writer = _h3()

    assert "dynv2. is the first line." in instruction
    assert "Write it for most scenes." in instruction
    assert "Leave it out only if the scene is calm or still." in instruction
    assert "[Shot 1] dynv2" not in instruction


def test_the_h3_instruction_asks_for_the_three_sections():
    """H3's prompt is sectioned, and the sound comes from the same pass -- so the writer writes the
    soundscape too."""
    instruction, _writer = _h3()

    for said in ("integrated_multimodal_description:", "overall_soundscape:",
                 "non_diegetic_music: N/A"):
        assert said in instruction, said


def _loop_rule():
    from backend.features.photo_generation.data import xai_prompt_writer
    return xai_prompt_writer.LOOP_RULE


def test_a_loop_video_is_asked_for_a_motion_that_returns():
    """Madde 307: the clip is played several times back to back, and the model slowing down to land
    on the last frame is what reads as a pulse. A motion that returns arrives by its own rhythm."""
    _instruction, writer = _h3()
    client = FakeClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "loop")

    assert _loop_rule() in client.calls[0][0]


def test_a_plain_video_is_asked_for_nothing_extra():
    instruction, writer = _h3()
    client = FakeClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "standard")

    assert client.calls == [(instruction, "kırmızı elbiseli kadın")]


def test_wan_asks_for_the_same_returning_motion():
    # Loop is a mode of both engines, so the rule belongs to both writers -- as one sentence.
    client = FakeClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "loop")

    assert _loop_rule() in client.calls[0][0]


def test_the_loop_rule_says_what_it_wants_and_what_it_refuses():
    # The whole of the fix is in these words: a cycle, not a movement that ends.
    rule = _loop_rule()

    assert "returns" in rule and "loop" in rule.lower()
    assert "does not end" in rule or "not a motion that ends" in rule


def test_the_sound_writer_takes_the_mode_and_ignores_it():
    """One call shape: the loop hands every writer the same arguments, and a sound is laid over the
    whole of a video however that video was made."""
    client = FakeClient(answer="fabric rustling")

    written = AudioPromptWriter(client).write({"photo": "a", "video": "b"}, "loop")

    assert written == "fabric rustling"
    assert "loop" not in client.calls[0][0].lower()
