"""How a video job says where it ends.

Three identities and nothing else. What the user reads in Turkish is the frontend's business: a name
and its label pulled apart on purpose, so renaming one on screen never touches what is written in a
plan file that has to keep reading back for months.

Only a video has a mode. A photo is made from its words and a sound is laid over the whole of a
video -- neither arrives anywhere, so neither is asked.
"""
STANDARD = "standard"
LOOP = "loop"
LINKED = "linked"

# What the queue validates against. A mode missing from here could never be asked for.
ALL = (STANDARD, LOOP, LINKED)


def of(job):
    """The mode a planned job carries, as the engine should read it.

    Anything the list does not know reads as the plain one, and so does a job with no mode at all:
    every video planned before this madde carries none, and each has to go on rendering exactly as
    it does today. The queue refuses an unknown mode at the door, so by the time a job is being
    rendered the plain reading is the only honest one left.
    """
    mode = job.get("mode")
    return mode if mode in ALL else STANDARD
