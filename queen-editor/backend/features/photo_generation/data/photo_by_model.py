"""The photo producer the queue is handed: each frame goes to the producer of its model's graph.

A model with a graph of its own -- Krea 2 Turbo (madde 482), Qwen Image 2.1 Turbo (madde 499) -- is
named in `own`. Every other value goes to `default`, the producer that has always made the photos: a
checkpoint model, an empty model, an old `recipe:` value and a bare file name alike, so every frame
planned before Krea renders where it always did.
"""


class PhotoByModel:
    def __init__(self, default, own):
        self._default = default
        self._own = own

    def _for(self, model):
        return self._own.get(model, self._default)

    def generate(self, prompt, negative, seed, model="", lora="", **rest):
        """Whatever else the queue hands a producer (ports.PhotoGenerator) goes through untouched."""
        return self._for(model).generate(prompt, negative, seed, model, lora, **rest)

    def fits_batch(self, count, model=""):
        """Asked of the model's producer. One with no batch makes its variants one by one."""
        producer = self._for(model)
        return hasattr(producer, "fits_batch") and producer.fits_batch(count, model)

    def generate_batch(self, prompt, negative, seed, count, model="", lora="", orientation=None):
        return self._for(model).generate_batch(prompt, negative, seed, count, model, lora,
                                               orientation=orientation)
