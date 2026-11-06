"""What the agent's context is allowed to take, in bytes of the JSON answer (FOUNDATION 4).

About four bytes make a token of English. A change that needs more raises the number here, with its
reason, so a reviewer sees the context grow.
"""

# v1's ~45 endpoints at ~65 B a line, nine sections of two or three sentences, the rules: ~5.3 KB.
INDEX_BYTES = 6144
# One endpoint's line in the index, "GET /address: a summary of a few words", quoted.
INDEX_LINE_BYTES = 96
# One address's detail, every method at it; v1's largest, t2i's, takes ~10 fields and answers a job.
DETAIL_BYTES = 4096
# One item of a list with its default fields, the worst built from the document's schema
# (tests/lists/test_listing.py). Step 6's largest default set is the frames': two ids, a scene and
# two statuses, ~230 B. A page of 100 is then at most ~25 KB.
LIST_ITEM_BYTES = 256
# The worst item's free text, where the schema sets no maxLength: a scene of a sentence or two.
TEXT_SAMPLE_BYTES = 120
# One error: a code, a sentence, the ids it is about and a hint; the first six problems listed, cut
# (core/errors.py), the rest counted. Whatever the request: the worst the tests send is ~1.3 KB.
ERROR_BYTES = 2048
