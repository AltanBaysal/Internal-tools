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
# One error: a code, a sentence, the ids it is about and a hint; the first six problems listed, cut
# (core/errors.py), the rest counted. Whatever the request: the worst the tests send is ~1.3 KB.
ERROR_BYTES = 2048
