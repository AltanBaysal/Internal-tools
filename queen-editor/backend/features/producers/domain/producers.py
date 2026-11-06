"""The two producers, in the order the engine works in. Sound had the third until MMAudio went
(madde 514); a sound already made is a layer like any other, and nothing makes a new one.

The ids are the layer names the rest of the app already uses, so a job's type is also the name of
the producer that can do it -- no translation table in between.
"""
PHOTO = "photo"
VIDEO = "video"

ORDER = (PHOTO, VIDEO)
NAMES = {PHOTO: "Fotoğraf üreticisi", VIDEO: "Video üreticisi"}
# What the video panel's Model box calls the one video model there is (madde 247, 435).
VIDEO_MODEL = "MiniMax H3"
