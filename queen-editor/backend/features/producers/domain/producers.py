"""The three producers, in the order the engine works in.

The ids are the layer names the rest of the app already uses, so a job's type is also the name of
the producer that can do it -- no translation table in between.
"""
PHOTO = "photo"
VIDEO = "video"
AUDIO = "audio"

ORDER = (PHOTO, VIDEO, AUDIO)
NAMES = {PHOTO: "Fotoğraf üreticisi", VIDEO: "Video üreticisi", AUDIO: "Ses üreticisi"}
