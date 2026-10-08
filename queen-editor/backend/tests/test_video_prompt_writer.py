import importlib.util
import os
import re

import pytest

from backend.features.photo_generation.data import prompt_writer
from backend.features.photo_generation.data.prompt_writer import (
    AUDIO_INSTRUCTION,
    AudioPromptWriter,
)

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
QUEEN_AGENT_PROMPT = os.path.join(os.path.dirname(TOOL), "queen-agent", "backend", "features",
                                  "workspace", "domain", "prompt.py")


# Madde 400: Queen AI is shown the frame's photo and reads its scenario.
PHOTO = ("P0_0.png", b"PNGDATA")
THRONE = "Kraliçe tahtında oturuyor; salon boş ve karanlık."

# Madde 402: a linked video's writer sees the photo the video ends on too.
NEXT = ("P1_0.png", b"NEXTDATA")


class FakeQueenAI:
    """Queen AI's box, without DeepSeek: records each ask as (instruction, words, pictures) and
    answers with what the test set up -- a prompt, or the failure the box gave up with."""

    def __init__(self, answer="integrated_multimodal_description: [Shot 1] she turns",
                 failed=False):
        self.answer = answer
        self.failed = failed
        self.calls = []

    def ask(self, system, text="", images=()):
        # Imported here rather than at the top: a module that cannot be imported would fail
        # collection, and pytest stops the whole session on a collection error.
        from backend.services.deepseek.box import Answer
        self.calls.append((system, text, list(images)))
        return Answer(self.answer, failed=self.failed)


def _sent(instruction):
    """What a writer hands Queen AI as its system message: its own text, then the suffix (madde
    407)."""
    return instruction + prompt_writer.SYSTEM_PROMPT_SUFFIX


def _queen_agent_suffix():
    """QueenAgent's suffix, the value QueenAgent sends.

    Its module is loaded rather than parsed, so the value is read however the owner writes it. The
    module imports nothing, by its own rule, so loading it brings nothing else of QueenAgent's here.
    """
    spec = importlib.util.spec_from_file_location("queen_agent_prompt", QUEEN_AGENT_PROMPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SYSTEM_PROMPT_SUFFIX


def test_no_wan_writer_is_left():
    """Madde 435: H3 is the one video model, so Queen AI is asked for H3's prompt and the sound's --
    WAN's text and its writer went with WAN."""
    assert not hasattr(prompt_writer, "VideoPromptWriter")
    assert not hasattr(prompt_writer, "VIDEO_INSTRUCTION")


def test_the_sound_is_written_from_the_video_s_prompt_alone():
    """The user's words (1 Ekim): "mmaudio da video promptundan alsın". No picture and none of the
    photo's words: the video's prompt already says what happens."""
    client = FakeQueenAI(answer="fabric rustling, footsteps on stone")

    written = AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın",
                                              "video": "kadın başını çeviriyor"})

    assert written == "fabric rustling, footsteps on stone"
    assert client.calls == [(_sent(AUDIO_INSTRUCTION), "Video prompt: kadın başını çeviriyor",
                             [])]


def test_the_sound_text_writes_from_the_video_prompt():
    assert "The video prompt says what happens in the video." in AUDIO_INSTRUCTION
    assert "Write only the sounds the video prompt implies." in AUDIO_INSTRUCTION


def test_the_sound_instruction_asks_for_the_scenes_own_sounds():
    assert "No music" in AUDIO_INSTRUCTION
    assert "No speech" in AUDIO_INSTRUCTION


def _h3():
    """Imported where it is used: a name that is not there would fail collection and take the sound
    questions above down with it."""
    from backend.features.photo_generation.data import prompt_writer
    return prompt_writer.H3_VIDEO_INSTRUCTION, prompt_writer.H3VideoPromptWriter


def test_the_h3_writer_shows_queen_ai_the_photo_and_the_scenario():
    """The model sees the picture the tags drew, so the tags themselves are not sent."""
    instruction, writer = _h3()
    client = FakeQueenAI()

    written = writer(client).write({"photo": "score_9_up, 1girl, queen"}, "standard",
                                   source=PHOTO, scene=THRONE)

    assert written == "integrated_multimodal_description: [Shot 1] she turns"
    assert client.calls == [(_sent(instruction), f"Scenario: {THRONE}", [PHOTO])]


def test_a_frame_with_no_scenario_sends_the_photo_alone():
    """The H3 text says what to do then: a small, natural motion for the picture."""
    instruction, writer = _h3()
    client = FakeQueenAI()

    writer(client).write({"photo": "score_9_up, 1girl, queen"}, "standard", source=PHOTO,
                         scene="")

    assert client.calls == [(_sent(instruction), "", [PHOTO])]


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
    client = FakeQueenAI()

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


# --- Madde 421: the H3 text says no length -------------------------------------------------------

# A length said in seconds: a number -- in figures or in words -- before "second(s)" or "sec(s)", or
# the word "seconds" on its own. "one to four sentences" is a count of sentences and "the second
# photo" an order, so neither is one.
LENGTH = re.compile(r"\b(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven"
                    r"|twelve)[\s-]*(?:seconds?|secs?)\b|\bseconds\b", re.IGNORECASE)


def test_the_h3_text_says_no_length_in_any_mode():
    """The user's words (v9-1, 5 Ekim): "bence videoda uzunluk belirtemyelim h3 te olur mu bu kritik
    bir bilg idğeil gerekirse geri getirirz". How long the video runs is the project's choice alone
    (madde 422). Asked of what the writer actually sends, so no rule appended to the text can bring a
    length back."""
    _instruction, writer = _h3()
    client = FakeQueenAI()

    for mode in ("standard", "loop", "linked"):
        writer(client).write({"photo": "kırmızı elbiseli kadın"}, mode, source=PHOTO, end=NEXT,
                             scene=THRONE)

    for sent, _words, _pictures in client.calls:
        said = LENGTH.findall(sent)
        assert said == [], f"H3 metni hâlâ bir uzunluk söylüyor: {said}"


def test_the_two_sentences_that_said_a_length_keep_the_rest_of_their_words():
    """Madde 421 takes the length out and nothing else: the context still says what H3 makes, and the
    rule still says how far to write -- to the end of the video, however long the project makes
    it."""
    instruction, _writer = _h3()

    assert "- H3 makes a video, with sound, from a photo.\n" in instruction
    assert "from the first frame to the end of the video.\n" in instruction


def _loop_rule():
    from backend.features.photo_generation.data import prompt_writer
    return prompt_writer.LOOP_RULE


def test_a_loop_video_is_asked_for_a_motion_that_returns():
    """Madde 307: the clip is played several times back to back, and the model slowing down to land
    on the last frame is what reads as a pulse. A motion that returns arrives by its own rhythm."""
    instruction, writer = _h3()
    client = FakeQueenAI()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "loop", source=PHOTO, scene="")

    assert client.calls[0][0] == _sent(instruction + _loop_rule())


def test_a_plain_video_is_asked_for_nothing_extra():
    instruction, writer = _h3()
    client = FakeQueenAI()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "standard", source=PHOTO,
                         scene="")

    # The suffix rides on every mode (madde 407); a plain video adds no rule of its own.
    assert client.calls[0][0] == _sent(instruction)


def _linked_rule():
    from backend.features.photo_generation.data import prompt_writer
    return prompt_writer.LINKED_RULE


def test_a_linked_video_shows_queen_ai_both_pictures_in_order():
    """Madde 402: the video ends on the next frame's photo, so the model is shown where it has to
    arrive -- this frame's photo first, as Picture 1, then the next one's, as Picture 2."""
    instruction, writer = _h3()
    client = FakeQueenAI()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "linked", source=PHOTO, end=NEXT,
                         scene=THRONE)

    assert client.calls == [(_sent(instruction + _linked_rule()), f"Scenario: {THRONE}",
                             [PHOTO, NEXT])]


def test_the_linked_text_calls_the_next_photo_picture_2_and_ends_on_it():
    rule = _linked_rule()

    assert "call the second photo Picture 2" in rule
    assert "Picture 2 is the last frame of the video." in rule


def test_the_linked_text_asks_for_the_changes_in_detail():
    """The user's words (v8-3, 29 Eylül): today a linked video joins "uc uca eklem gibi", and a
    transition written in detail is what the video model follows."""
    rule = _linked_rule()

    assert "Write the changes in detail, so the video flows into Picture 2 and never jumps." in rule
    assert "Never describe the two photos again." in rule


def test_a_loop_video_shows_its_picture_once():
    """A loop ends on its own photo -- the one already shown -- so it is not sent a second time, and
    nothing of the linked text reaches it."""
    instruction, writer = _h3()
    client = FakeQueenAI()

    writer(client).write({"photo": "kırmızı elbiseli kadın"}, "loop", source=PHOTO, end=PHOTO,
                         scene="")

    assert client.calls == [(_sent(instruction + _loop_rule()), "", [PHOTO])]


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
    client = FakeQueenAI(answer="fabric rustling")

    written = AudioPromptWriter(client).write({"photo": "a", "video": "b"}, "loop")

    assert written == "fabric rustling"
    assert "loop" not in client.calls[0][0].lower()


def test_the_sound_is_shown_no_picture_whatever_it_is_handed():
    """The loop hands every writer the same arguments; the sound's takes the video's prompt alone."""
    client = FakeQueenAI(answer="fabric rustling")

    AudioPromptWriter(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                    "standard", source=("P0_0_V1_0.mp4", b"MP4"), end=NEXT,
                                    scene=THRONE)

    assert client.calls == [(_sent(AUDIO_INSTRUCTION), "Video prompt: kadın dönüyor", [])]


def test_the_suffix_is_queen_agent_s_word_for_word():
    """Madde 407: the same text QueenAgent ends its system prompt with -- the user's "evet" (30
    Eylül). A copy, pinned: the owner rewrites QueenAgent's suffix by hand, and this goes red that
    day until the copy follows."""
    assert prompt_writer.SYSTEM_PROMPT_SUFFIX == _queen_agent_suffix(), (
        "Queen Editor'ün suffix'i QueenAgent'ınkiyle aynı değil: queen-agent/backend/features/"
        "workspace/domain/prompt.py'deki SYSTEM_PROMPT_SUFFIX, queen-editor/backend/features/"
        "photo_generation/data/prompt_writer.py'ye aynen kopyalanmalı"
    )


def test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix():
    """Madde 407, as its done-sentence says it: whichever prompt Queen AI writes -- H3 or the sound
    -- and in whichever mode, the system prompt it is handed ends with QueenAgent's suffix. Asked of
    QueenAgent's text rather than the copy."""
    _instruction, h3 = _h3()
    client = FakeQueenAI()

    for writer in (h3, AudioPromptWriter):
        for mode in ("standard", "loop", "linked"):
            writer(client).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                 mode, source=PHOTO, end=NEXT, scene=THRONE)

    suffix = _queen_agent_suffix()
    for sent, _words, _pictures in client.calls:
        assert sent.endswith(suffix), f"System prompt suffix'le bitmiyor:\n{sent}"


# --- Madde 416: the box's failure ----------------------------------------------------------------

@pytest.mark.parametrize("kind", ["h3", "sound"])
def test_a_failed_answer_is_never_a_prompt(kind):
    """When the box gave up it says why in its text, and that text goes the way any failure goes --
    raised into the run loop, never written on the card as the prompt."""
    writer = {"h3": _h3()[1], "sound": AudioPromptWriter}[kind]
    queen_ai = FakeQueenAI(answer="DeepSeek HTTP 503\nmeşgul", failed=True)

    with pytest.raises(RuntimeError) as failed:
        writer(queen_ai).write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                               "standard", source=PHOTO, scene=THRONE)

    assert str(failed.value) == "DeepSeek HTTP 503\nmeşgul"
