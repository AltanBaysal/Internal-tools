"""The photo producer the queue is handed (madde 482): each frame goes to the producer of its model's
graph -- Krea 2 Turbo to its own, every other value to the one that always made the photos."""
import pytest

from backend.features.photo_generation.data.photo_by_model import PhotoByModel


class Producer:
    """Writes down every call it gets, under its own name."""

    def __init__(self, name, calls):
        self.name, self.calls = name, calls

    def generate(self, prompt, negative, seed, model="", lora="", **rest):
        self.calls.append((self.name, "generate", prompt, negative, seed, model, lora, rest))
        return self.name.encode()


class Batching(Producer):
    def __init__(self, name, calls, fits):
        super().__init__(name, calls)
        self.fits = fits

    def fits_batch(self, count, model=""):
        self.calls.append((self.name, "fits_batch", count, model))
        return self.fits

    def generate_batch(self, prompt, negative, seed, count, model="", lora="", orientation=None):
        self.calls.append((self.name, "generate_batch", prompt, negative, seed, count, model, lora,
                           orientation))
        return [self.name.encode()] * count


def over(fits=True):
    calls = []
    return calls, PhotoByModel(Batching("sdxl", calls, fits), {"krea2": Producer("krea", calls)})


def test_a_krea_frame_goes_to_krea_with_everything_the_queue_handed():
    calls, photo = over()

    made = photo.generate("p", "blurry", 7, "krea2", "usnr", source=None, orientation="yatay")

    assert made == b"krea"
    assert calls == [("krea", "generate", "p", "blurry", 7, "krea2", "usnr",
                      {"source": None, "orientation": "yatay"})]


@pytest.mark.parametrize("model", ["", "nova3dcg", "dasiwa", "recipe:slime",
                                   "nova3DCGXL_ilV90.safetensors"])
def test_every_other_value_goes_where_it_always_went(model):
    """Empty, an old recipe and a bare file name included: the producer that has always made the
    photos keeps reading them the way it did."""
    calls, photo = over()

    assert photo.generate("p", "", 7, model, "") == b"sdxl"
    assert calls[0][:2] == ("sdxl", "generate")


def test_krea_makes_its_variants_one_by_one():
    """Krea has no batch: the question is never put to the other producer's card."""
    calls, photo = over(fits=True)

    assert photo.fits_batch(4, "krea2") is False
    assert calls == []


@pytest.mark.parametrize("fits", [True, False])
def test_the_card_question_goes_to_the_model_s_producer(fits):
    calls, photo = over(fits=fits)

    assert photo.fits_batch(4, "nova3dcg") is fits
    assert calls == [("sdxl", "fits_batch", 4, "nova3dcg")]


def test_a_batch_goes_to_the_model_s_producer():
    calls, photo = over()

    made = photo.generate_batch("p", "n", 7, 3, "dasiwa", "slime", orientation="dikey")

    assert made == [b"sdxl"] * 3
    assert calls == [("sdxl", "generate_batch", "p", "n", 7, 3, "dasiwa", "slime", "dikey")]
