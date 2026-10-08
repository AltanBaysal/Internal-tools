"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol


class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int, model: str = "", lora: str = "",
                 source: tuple | None = None, end: tuple | None = None,
                 references: tuple = (), seconds: int | None = None,
                 happy_ending: bool = False) -> bytes:
        """Render one layer and return its bytes -- nothing else, and no name.

        `source` is the file this layer is made from as (name, bytes): a video's photo, a sound's
        video. A layer made from its words alone is given None, and every producer takes the
        argument whether it uses it or not -- the queue has one call shape, not three.

        `end` is the picture the layer arrives at, same shape. Only a video has one; a photo and a
        sound take the argument and ignore it, for the same reason `source` is taken by all three.

        `references` is the project's reference pool as (name, bytes, kind), in the pool's own
        order -- only a video made from it has any (madde 304).

        The file's name is the domain's (photo_name.layer_file), never the producer's.

        An empty model means the graph's own default, and an empty lora means the default lora.
        Only a photo has either; a video and a sound take both and ignore them, like `end`.

        `seconds` is how long a video should run, from its job (madde 422). Only a video job
        carries one; a photo and a sound take it and ignore it, like `end`. None is a job that
        carries none, and its graph's own length stands. How long the video then runs is the
        producer's to say (VideoGenerator.seconds).

        `happy_ending` is whether the video ends happily, from its job (madde 426): H3 loads
        HMCumshot for it. A photo and a sound take it and ignore it, like `seconds`.
        """
        ...


class BatchPhotoGenerator(PhotoGenerator, Protocol):
    """A photo producer that can also make a prompt's variants in one job (madde 411). The loop asks
    these only of a producer that has them -- a video's and a sound's do not -- and makes the
    variants one by one otherwise."""

    def fits_batch(self, count: int) -> bool:
        """Whether the card holds `count` pictures of one prompt in one batch."""
        ...

    def generate_batch(self, prompt: str, negative: str, seed: int, count: int, model: str = "",
                       lora: str = "") -> list:
        """`count` pictures of one prompt from one seed, as bytes, in the batch's order."""
        ...


class VideoGenerator(PhotoGenerator, Protocol):
    """A video producer: it also says how long the videos it makes run (madde 423). The loop asks it
    of the video producer alone, and writes the answer on the video's row."""

    def seconds(self, asked: int | None = None) -> float:
        """How long a video asked to run `asked` seconds comes out. None -- a job that asked for no
        length -- is the graph's own, which is also what the export summary counts a row that says
        no length at."""
        ...


class PromptWriter(Protocol):
    def write(self, prompts: dict, mode: str, source: tuple | None = None,
              end: tuple | None = None, scene: str = "", happy_ending: bool = False) -> str:
        """The prompt a job of this type should be produced with.

        `prompts` is what the frame already says: {"photo": …} today, plus the video's own when
        audio joins. Raising is a failure like any other -- the loop's three attempts and its
        frame-fault rule apply to it unchanged.

        `mode` is how the job is being produced (domain/production_mode.py). A loop video has to be
        asked for a motion that returns (madde 307); a sound takes the argument and ignores it, the
        way every producer takes `references`.

        `source` is the file the layer is made from as (name, bytes) -- the one its producer is
        handed -- and `scene` is the frame's scenario, empty for a frame that has none. H3's writer
        shows the model both (madde 400); the others take them and ignore them, for the same one
        call shape.

        `end` is the picture the video arrives at -- the one its producer is handed as `end` -- or
        None. H3's writer shows it to the model for a linked video (madde 402); the others take it
        and ignore it.

        `happy_ending` is whether the video's job carries Mutlu son (madde 426). H3's writer then asks
        for the ending; the sound's takes it and ignores it.
        """
        ...


class Stills(Protocol):
    def first_frame(self, video: bytes) -> bytes:
        """The video's opening frame, as the bytes of a picture.

        What a card with no photo gets when its video lands (madde 296). Raising is not a failure of
        the job: the video is made and its row is written, and the picture is a convenience.
        """
        ...


class ReferenceStore(Protocol):
    def save(self, project: str, name: str, data: bytes) -> None:
        """Put one reference in the project's pool, under the name the domain chose."""
        ...

    def items(self, project: str) -> list:
        """[(name, seconds)] for every file in the pool, in one stable order -- by name.

        Not the order they were written in: a file's timestamp is coarser than the writes, so two
        files of one upload sometimes share one, and the pool would read back differently on two
        machines. Which order the USER wants them in is a different question, and it gets a
        document of its own (madde 300).

        `seconds` is None for anything with no length -- a picture, or a file the pool cannot read.
        It is taken off the file every time rather than remembered, so a reference replaced in
        Drive counts as what it now is.
        """
        ...

    def read(self, project: str, name: str) -> bytes | None:
        """One reference's bytes; None when it is not there."""
        ...

    def delete(self, project: str, name: str) -> None:
        """Take one out; a name that is not there is not an error."""
        ...


class PhotoStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def next_number(self, project: str) -> int:
        """Highest existing number + 1, so nothing is ever overwritten."""
        ...

    def save(self, project: str, filename: str, data: bytes) -> str:
        """Persist the photo under the name the domain chose; returns that name."""
        ...

    def read(self, project: str, filename: str) -> bytes | None:
        """The file's bytes; None when it is not there."""
        ...

    def delete(self, project: str, filename: str) -> None:
        """Remove the photo from the project folder; a missing file is not an error."""
        ...

    def photo_dir(self, project: str) -> str:
        """Absolute folder the photos live in -- presentation serves files from it."""
        ...


class PlanStore(Protocol):
    def read(self, project: str) -> dict:
        """{"negative", "frames"} -- the queue as stored, every frame carrying its identity and its
        negative."""
        ...

    def append(self, project: str, frames: list) -> None:
        """Put frames at the end of the queue, in render order."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the stored plan reserved; None when there is no plan."""
        ...


class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced layer's row."""
        ...

    def list(self, project: str) -> list:
        """Every photo that still exists, newest first."""
        ...

    def mark(self, project: str, frame: str, layer: str, file: str, status: str, at: str,
             error: str | None = None) -> None:
        """Append a line for an event that produced no layer."""
        ...

    def prompt_written(self, project: str, frame: str, layer: str, file: str, prompt: str,
                       at: str) -> None:
        """Keep the prompt a model wrote for a layer still owed, on the card, until it is made."""
        ...

    def written_prompts(self, project: str) -> dict:
        """{frame: {layer: prompt}} -- the prompts written for layers still owed. A later line about
        the layer -- produced, failed, removed, deleted or put back in line -- ends it."""
        ...

    def slots(self, project: str) -> dict:
        """{frame: {slot: {"status", "file"[, "error"][, "renderSeconds"][, "seconds"]}}} -- the
        latest line per (frame, slot).

        "error" is there only where the line carried one, which is only on a failure.
        "renderSeconds" only on a layer produced since madde 405: the seconds the model worked on it.
        "seconds" on a video produced since madde 423 (an H3 one since 422): how long it runs.
        """
        ...

    def prompts(self, project: str) -> dict:
        """{frame: {layer: prompt}} -- what each layer was made from; the latest line wins. A layer
        still owed says the prompt written for it."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the record has ever seen, whatever became of the frame."""
        ...


class OrderStore(Protocol):
    def read(self, project: str) -> list:
        """The stored gallery order as frame identities; empty when there is none."""
        ...

    def write(self, project: str, order: list) -> None:
        """Replace the project's gallery order."""
        ...


class VideoLengthStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def read(self, project: str) -> int | None:
        """How long the project's H3 videos run, in seconds; None when nothing usable is saved."""
        ...

    def write(self, project: str, seconds: int) -> None:
        """Replace the saved length."""
        ...


class HappyEndingStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def read(self, project: str) -> bool | None:
        """The project's Mutlu son switch; None when nothing usable is saved."""
        ...

    def write(self, project: str, on: bool) -> None:
        """Replace the saved switch."""
        ...
