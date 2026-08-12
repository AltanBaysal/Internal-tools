from backend.features.photo_generation.data.xai_prompt_writer import (
    INSTRUCTION,
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
    assert client.calls == [(INSTRUCTION, "kırmızı elbiseli kadın")]


def test_the_instruction_says_what_wan_needs_and_what_to_leave_out():
    # The rules are the whole value of this file: a drifted instruction is a wrong prompt.
    assert "image-to-video" in INSTRUCTION
    assert "Keep the camera static" in INSTRUCTION
    assert "Output only the motion prompt itself" in INSTRUCTION
