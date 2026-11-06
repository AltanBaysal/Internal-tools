"""`like` and `ilike`'s pattern: PostgREST's, `*` any run of characters, the pattern the whole text.

No regex engine: compiling a single pattern from a query filled this machine's 16 GB (530), and a
time limit bounds matching, not compiling. Here the pattern is cut on its `*`s and matched in one
pass, O(L·m) for a text of L characters and pieces of m characters, linear in L. A pattern is at
most MOST_CHARACTERS as written; `ilike`'s casefold can lengthen it (`ß` is `ss`, `ﬃ` is `ffi`),
so a folded piece is at most three times that. `*` has no escape, so it cannot itself be searched
for. Pure.
"""

from dataclasses import dataclass

# Step 6: a pattern is at most 200 characters as the caller writes it.
MOST_CHARACTERS = 200

# `ilike` finds Turkish and English alike: the four i's are one letter (step 6).
_FOUR_IS = str.maketrans({"I": "i", "ı": "i", "İ": "i"})


def fold(text: str) -> str:
    """`ilike`'s case: the four i's as one, then Unicode's casefold (`Ğ` is `ğ`, `ß` is `ss`)."""
    # Before casefold, which makes `İ` an `i` and a combining dot.
    return text.translate(_FOUR_IS).casefold()


class TooLong(ValueError):
    """A pattern over MOST_CHARACTERS."""


@dataclass(frozen=True)
class Pattern:
    pieces: tuple[str, ...]  # the text between the `*`s, folded for `ilike`
    folded: bool

    @classmethod
    def read(cls, text: str, folded: bool) -> "Pattern":
        """Raises TooLong past MOST_CHARACTERS, before anything is matched."""
        if len(text) > MOST_CHARACTERS:
            raise TooLong(f"a pattern has at most {MOST_CHARACTERS} characters")
        return cls(tuple((fold(text) if folded else text).split("*")), folded)

    def matches(self, text: str) -> bool:
        """The first piece starts the text, the last ends it, each between is found after the one
        before: the leftmost place is as good as any, so there is no backtracking."""
        if self.folded:
            text = fold(text)
        if len(self.pieces) == 1:
            return text == self.pieces[0]
        first, *between, last = self.pieces
        end = len(text) - len(last)
        if end < len(first) or not text.startswith(first) or not text.endswith(last):
            return False
        at = len(first)
        for piece in between:
            found = text.find(piece, at, end)
            if found < 0:
                return False
            at = found + len(piece)
        return True
