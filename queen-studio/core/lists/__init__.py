"""The query every list takes (step 6, List query): PostgREST's syntax, run over records in memory.

`fields` reads a list's fields off the model of its items, `parse` reads a query against them,
`run` applies it to the records, and `listing` declares a list and joins it to FastAPI. Only
`listing` knows FastAPI.
"""
