"""Which models can render right now.

One line of forwarding on purpose: the answer is the renderer's, and the app keeps no list of its
own. A second list would disagree with the notebook the first time a model is added there, and the
user would be offered a model that is not installed -- or not offered one that is.

Nothing is validated or sorted here: the order the renderer lists them in is the order the panel
shows, so what the user picks from is exactly what the graph can load.
"""


def list_models(generator):
    return generator.models()
