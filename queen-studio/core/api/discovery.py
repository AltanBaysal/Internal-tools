"""`GET /api`'s two answers, read from the API's OpenAPI document (step 6, Discovery).

The index is the agent's first read: the rules once, then each section with one line per
endpoint, so an endpoint added grows it by one line. An address's detail gives what each method
there takes and returns, for the one address the agent is about to call. Both come out of the code
that serves the addresses, so neither can drift from it. Pure: a document in, an answer out.
"""

from typing import Any

Json = dict[str, Any]

RULES = (
    "Every address is under /api, written here without it. Bodies and answers are JSON; a field an "
    "address does not take is an error, never dropped. Success is always 200. An error is {code, "
    "message, details, hint}: act on code; details holds the ids, and details.problems each "
    "problem; hint is the next step, or null. GET /api?path=<address> gives what each method at "
    "that address takes and returns."
)

# What a field's schema says that the agent acts on; titles and the rest of JSON Schema stay out.
_KEPT = (
    "description",
    "enum",
    "const",
    "default",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "pattern",
    "minItems",
    "maxItems",
)


def index(doc: Json) -> Json:
    """Raises ValueError for an operation in no section: left out, the agent would never find it."""
    sections: dict[str, Json] = {
        tag["name"]: {"name": tag["name"], "about": tag["description"], "endpoints": []}
        for tag in doc.get("tags", [])
    }
    for path, item in doc["paths"].items():
        for method, operation in item.items():
            tags: list[str] = operation.get("tags", [])
            if len(tags) != 1 or tags[0] not in sections:
                raise ValueError(
                    f"{method.upper()} {path} is in no section of the index: give its router one "
                    "of the tags create_api names in openapi_tags."
                )
            # A plain line, not an object: the three keys repeated on every line cost ~30 B each.
            sections[tags[0]]["endpoints"].append(
                f"{method.upper()} {path}: {operation['summary']}"
            )
    return {
        "app": doc["info"]["title"],
        "version": doc["info"]["version"],
        "rules": RULES,
        "sections": [section for section in sections.values() if section["endpoints"]],
    }


def detail(doc: Json, address: str) -> Json | None:
    """Each method at `address`, as the index writes it; None when there is no such address."""
    item = doc["paths"].get(address)
    if item is None:
        return None
    return {method.upper(): _method(operation, doc) for method, operation in item.items()}


def _method(operation: Json, doc: Json) -> Json:
    found: Json = {}
    if "description" in operation:
        found["description"] = operation["description"]
    # Headers stay out: the MCP tool and the UI add them, the agent never writes one (step 6).
    for place in ("path", "query"):
        fields = {
            parameter["name"]: _field(
                {**parameter["schema"], **_described(parameter)},
                doc,
                inputs=True,
                required=parameter.get("required", False),
            )
            for parameter in operation.get("parameters", [])
            if parameter["in"] == place
        }
        if fields:
            found[place] = fields
    if "requestBody" in operation:
        schema = operation["requestBody"]["content"]["application/json"]["schema"]
        found["body"] = _field(schema, doc, inputs=True)
    answer = operation["responses"].get("200", {}).get("content", {}).get("application/json")
    if answer:
        found["returns"] = _field(answer["schema"], doc, inputs=False)
    if "x-errors" in operation:
        found["errors"] = operation["x-errors"]
    return found


def _described(parameter: Json) -> Json:
    return {"description": parameter["description"]} if "description" in parameter else {}


def _field(schema: Json, doc: Json, inputs: bool, required: bool | None = None) -> Json:
    """One field as the agent reads it: its type, if it is required (inputs only), what it is."""
    schema = _resolved(schema, doc)
    options = [_resolved(option, doc) for option in schema.get("anyOf", [])]
    real = [option for option in options if option.get("type") != "null"]
    if len(real) == 1:
        # `X | None`: the field is X's, nullable; its own description and default stay on top.
        schema = {**real[0], **{key: value for key, value in schema.items() if key != "anyOf"}}
    kinds = [option.get("type", "any") for option in options]
    found: Json = {"type": " | ".join(kinds) if kinds else schema.get("type", "any")}
    if required is not None:
        found["required"] = required
    found.update((key, schema[key]) for key in _KEPT if key in schema)
    if "properties" in schema:
        needed: list[str] = schema.get("required", [])
        found["fields"] = {
            name: _field(field, doc, inputs, (name in needed) if inputs else None)
            for name, field in schema["properties"].items()
        }
    if "items" in schema:
        found["items"] = _field(schema["items"], doc, inputs)
    return found


def _resolved(schema: Json, doc: Json) -> Json:
    if "$ref" not in schema:
        return schema
    target: Json = doc["components"]["schemas"][schema["$ref"].rsplit("/", 1)[1]]
    return {**target, **{key: value for key, value in schema.items() if key != "$ref"}}
