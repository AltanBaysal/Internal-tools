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


# Madde 400: Queen AI is shown the frame's photo and reads its scenario.
PHOTO = ("P0_0.png", b"PNGDATA")
THRONE = "Kraliçe tahtında oturuyor; salon boş ve karanlık."


class FakeVisionClient:
    """DeepSeek, without one: records each ask as (instruction, words, pictures)."""

    def __init__(self, answer="integrated_multimodal_description: [Shot 1] she turns"):
        self.answer = answer
        self.calls = []

    def complete(self, system, text="", images=()):
        self.calls.append((system, text, list(images)))
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


def test_the_h3_writer_shows_queen_ai_the_photo_and_the_scenario():
    """The model sees the picture the tags drew, so the tags themselves are not sent."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    written = writer(client).write({"photo": "score_9_up, 1girl, queen"}, "standard",
                                   source=PHOTO, scene=THRONE)

    assert written == "integrated_multimodal_description: [Shot 1] she turns"
    assert client.calls == [(instruction, f"Scenario: {THRONE}", [PHOTO])]


def test_a_frame_with_no_scenario_sends_the_photo_alone():
    """The H3 text says what to do then: a small, natural motion for the picture."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "score_9_up, 1girl, queen"}, "standard", source=PHOTO,
                         scene="")

    assert client.calls == [(instruction, "", [PHOTO])]


def test_the_h3_instruction_says_the_photo_is_the_first_frame():
    # The user's words (madde 246): the model is told plainly what the photo is to the video.
    instruction, _writer = _h3()

    assert "The photo is the first frame of the video." in instruction


def test_the_h3_instruction_never_asks_for_dynv2():
    """Madde 331: the writer leaves the trigger out of every scene -- the user's call, "hiç
    yazılmasın ... istediğin prompt'a elle eklersin". Asked of what the writer actually sends, loop
    included, so no rule appended to the instruction can bring the word back. Adding it by hand still
    works: the producer puts a leading dynv2 first (test_comfy_h3_video_generator)."""
    _instruction, writer = _h3()
    client = FakeVisionClient()

    for mode in ("standard", "loop", "linked"):
        writer(client).write({"photo": "kırmızı elbiseli kadın"}, mode, source=PHOTO,
                             scene=THRONE)

    for sent, _words, _pictures in client.calls:
        assert "dynv2" not in sent, f"Talimat hâlâ dynv2 istiyor:\n{sent}"


def test_the_h3_instruction_asks_for_the_three_sections():
    """H3's prompt is sectioned, and the sound comes from the same pass -- so the writer writes the
    soundscape too."""
    instruction, _writer = _h3()

    for said in ("integrated_multimodal_description:", "overall_soundscape:",
                 "non_diegetic_music: N/A"):
        assert said in instruction, said


def test_the_h3_text_asks_for_no_speech_where_the_scenario_has_none():
    """The user's words (v8-3, 29 Eylül): "özellikle konuşma belirtilmediyse senayoda o framede
    konuşma eklnemesin". H3 has no negative, so the prompt itself says there is none."""
    instruction, _writer = _h3()

    assert "write no speech at all" in instruction
    assert '"No one speaks."' in instruction


def test_the_h3_text_calls_the_photo_picture_1_and_leaves_the_first_line_to_the_code():
    """The producer opens the prompt with the line saying where each picture sits
    (comfy_h3_video_generator), and that line calls the photo Picture 1."""
    instruction, _writer = _h3()

    assert "call the photo Picture 1" in instruction
    assert "Never write the line." in instruction


def test_the_h3_text_says_what_to_do_without_a_scenario():
    instruction, _writer = _h3()

    assert "If no scenario is given, write a small, natural motion for Picture 1." in instruction


def _loop_rule():
    from backend.features.photo_generation.data import xai_prompt_writer
    return xai_prompt_writer.LOOP_RULE


def test_a_loop_video_is_asked_for_a_motion_that_returns():
    """Madde 307: the clip is played several times back to back, and the model slowing down to land
    on the last frame is what reads as a pulse. A motion that returns arrives by its own rhythm."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "loop", source=PHOTO, scene="")

    assert client.calls[0][0] == instruction + _loop_rule()


def test_a_plain_video_is_asked_for_nothing_extra():
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "standard", source=PHOTO,
                         scene="")

    assert client.calls[0][0] == instruction


def test_a_linked_video_gets_the_h3_text_alone_for_now():
    """Madde 402 adds what a linked video is asked for, with the next frame's photo; until then it
    is asked what a plain one is."""
    instruction, writer = _h3()
    client = FakeVisionClient()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "linked", source=PHOTO, scene="")

    assert client.calls[0][0] == instruction


def test_wan_asks_for_the_same_returning_motion():
    # Loop is a mode of both engines, so the rule belongs to both writers -- as one sentence.
    client = FakeClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "loop")

    assert _loop_rule() in client.calls[0][0]


def test_the_loop_rule_says_what_it_wants_and_what_it_refuses():
    # The whole of the fix is in these words: a motion that comes back, not one that comes to rest.
    rule = _loop_rule()

    assert "loop" in rule.lower() and "comes back to the first pose" in rule
    assert "shows as a stop each time the video starts again" in rule


def test_the_loop_rule_asks_for_one_speed_to_the_end():
    # Madde 315: most generators ease into the last frame, and the next repeat starts from rest. The
    # rule asks for the same speed all the way to the last frame -- the user's words, "hareket sonuna
    # kadar aynı hızda sürsün, sona doğru yavaşlamasın".
    rule = _loop_rule()

    assert "same speed" in rule and "slows down" in rule


def test_the_loop_rule_holds_the_camera_still():
    """Madde 400: the last frame is the first photo again, so a camera that moved would have to
    come back too -- and its return would show at the seam."""
    rule = _loop_rule()

    assert "The last frame is the first photo again" in rule
    assert "The camera holds a static shot." in rule


def test_the_sound_writer_takes_the_mode_and_ignores_it():
    """One call shape: the loop hands every writer the same arguments, and a sound is laid over the
    whole of a video however that video was made."""
    client = FakeClient(answer="fabric rustling")

    written = AudioPromptWriter(client).write({"photo": "a", "video": "b"}, "loop")

    assert written == "fabric rustling"
    assert "loop" not in client.calls[0][0].lower()


def test_wan_is_asked_as_before_whatever_else_it_is_handed():
    """The loop hands every writer the frame's photo and scenario -- one call shape -- and grok,
    which reads no picture, is asked exactly what it was asked before. 404 moves WAN."""
    client = FakeClient()

    VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"}, "standard",
                                    source=PHOTO, scene=THRONE)

    assert client.calls == [(VIDEO_INSTRUCTION, "kırmızı elbiseli kadın")]


def test_the_sound_is_asked_as_before_whatever_else_it_is_handed():
    client = FakeClient(answer="fabric rustling")

    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                    "standard", source=("P0_0_V1_0.mp4", b"MP4"), scene=THRONE)

    assert client.calls == [
        (AUDIO_INSTRUCTION, "Scene: kırmızı elbiseli kadın\nMotion: kadın dönüyor")]
