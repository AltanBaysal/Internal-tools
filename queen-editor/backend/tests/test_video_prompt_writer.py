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
