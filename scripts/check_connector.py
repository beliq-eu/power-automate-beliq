#!/usr/bin/env python3
"""Offline checks on the connector definition, its properties and the example bodies.

`paconn validate` is the vendor's own check but it authenticates against Power
Platform first, and it exits 0 when that login fails, so it cannot gate a pull
request. Everything below runs from the checkout alone and fails loudly.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft4Validator
from openapi_spec_validator import validate as validate_spec

ROOT = Path(__file__).resolve().parent.parent
CONNECTOR = ROOT / "Beliq"
SETTINGS = CONNECTOR / "settings.json"
SWAGGER = CONNECTOR / "apiDefinition.swagger.json"
PROPERTIES = CONNECTOR / "apiProperties.json"
EXAMPLES = ROOT / "example-flows"

# The example bodies are request payloads for this operation, so they are checked
# against the schema the connector publishes for it rather than against a copy.
EXAMPLE_OPERATION = "GenerateInvoice"

# A leftover development host would import cleanly and fail for every user.
EXPECTED_HOST = "api.beliq.eu"
EXPECTED_SCHEMES = ["https"]

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def json_files() -> list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*.json")
        if not any(part in {".venv", ".git", "node_modules"} for part in p.parts)
    )


def check_json_parses() -> dict[Path, object]:
    parsed: dict[Path, object] = {}
    for path in json_files():
        try:
            parsed[path] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{path.relative_to(ROOT)}: not valid JSON ({exc})")
    return parsed


def check_swagger_structure(swagger: dict) -> None:
    try:
        validate_spec(swagger)
    except Exception as exc:  # the validator raises several unrelated types
        fail(f"apiDefinition.swagger.json: not a valid Swagger 2.0 document ({exc})")


def check_settings_paths(settings: dict) -> None:
    for key in ("apiProperties", "apiDefinition", "icon"):
        name = settings.get(key)
        if not name:
            fail(f"settings.json: {key} is empty")
            continue
        if not (CONNECTOR / name).is_file():
            fail(f"settings.json: {key} points at Beliq/{name}, which does not exist")


def check_endpoint(swagger: dict) -> None:
    if swagger.get("host") != EXPECTED_HOST:
        fail(f"apiDefinition: host is {swagger.get('host')!r}, expected {EXPECTED_HOST!r}")
    if swagger.get("schemes") != EXPECTED_SCHEMES:
        fail(f"apiDefinition: schemes is {swagger.get('schemes')!r}, expected {EXPECTED_SCHEMES!r}")


def operations(swagger: dict):
    methods = {"get", "put", "post", "delete", "patch", "head", "options"}
    for path, item in swagger.get("paths", {}).items():
        for method, operation in item.items():
            if method.lower() in methods and isinstance(operation, dict):
                yield path, method.lower(), operation


def check_operations(swagger: dict) -> None:
    """Uniqueness of operationId is left to the spec validator, which enforces it."""
    for path, method, operation in operations(swagger):
        where = f"{method.upper()} {path}"
        operation_id = operation.get("operationId")
        if not operation_id:
            fail(f"{where}: no operationId")
            continue
        # Independent Publisher certification rejects an operation missing either.
        for field in ("summary", "description"):
            if not operation.get(field):
                fail(f"{where} ({operation_id}): no {field}")


def check_refs(swagger: dict) -> None:
    definitions = swagger.get("definitions", {})
    text = json.dumps(swagger)
    referenced = set(re.findall(r'"\$ref"\s*:\s*"#/definitions/([^"]+)"', text))
    for name in sorted(referenced - set(definitions)):
        fail(f"apiDefinition: $ref to #/definitions/{name}, which is not defined")

    # Reachability from the operations, so a definition orphaned by an edit is
    # caught here rather than by a reviewer noticing it months later.
    reachable: set[str] = set()
    frontier = {
        name
        for _, _, operation in operations(swagger)
        for name in re.findall(r'"\$ref"\s*:\s*"#/definitions/([^"]+)"', json.dumps(operation))
    }
    while frontier:
        name = frontier.pop()
        if name in reachable or name not in definitions:
            continue
        reachable.add(name)
        frontier |= set(
            re.findall(r'"\$ref"\s*:\s*"#/definitions/([^"]+)"', json.dumps(definitions[name]))
        )
    for name in sorted(set(definitions) - reachable):
        fail(f"apiDefinition: definition {name!r} is not reachable from any operation")


def check_auth_wiring(properties: dict, swagger: dict) -> None:
    props = properties.get("properties", {})
    declared = set(props.get("connectionParameters", {}))
    if not declared:
        fail("apiProperties: no connectionParameters declared")
    for instance in props.get("policyTemplateInstances", []):
        parameters = instance.get("parameters", {})
        for value in parameters.values():
            if not isinstance(value, str):
                continue
            for name in re.findall(r"connectionParameters\('([^']+)'\)", value):
                if name not in declared:
                    fail(
                        f"apiProperties: policy {instance.get('templateId')!r} reads "
                        f"connection parameter {name!r}, which is not declared"
                    )


def check_examples(swagger: dict, parsed: dict[Path, object]) -> None:
    target = None
    for _, _, operation in operations(swagger):
        if operation.get("operationId") == EXAMPLE_OPERATION:
            target = operation
            break
    if target is None:
        fail(f"apiDefinition: no operation {EXAMPLE_OPERATION!r} for the example bodies to match")
        return

    body = next(
        (p for p in target.get("parameters", []) if p.get("in") == "body"),
        None,
    )
    ref = (body or {}).get("schema", {}).get("$ref", "")
    name = ref.rsplit("/", 1)[-1]
    if name not in swagger.get("definitions", {}):
        fail(f"apiDefinition: {EXAMPLE_OPERATION} body schema {ref!r} does not resolve")
        return

    schema = dict(swagger["definitions"][name])
    schema["definitions"] = swagger["definitions"]
    validator = Draft4Validator(schema)

    found = sorted(p for p in parsed if p.parent == EXAMPLES)
    if not found:
        fail("example-flows: no example bodies found")
    for path in found:
        for error in sorted(validator.iter_errors(parsed[path]), key=lambda e: list(e.path)):
            location = "/".join(str(p) for p in error.path) or "(root)"
            fail(f"{path.relative_to(ROOT)}: {location}: {error.message}")


def main() -> int:
    parsed = check_json_parses()
    if failures:
        report()
        return 1

    swagger = parsed[SWAGGER]
    check_swagger_structure(swagger)
    check_settings_paths(parsed[SETTINGS])
    check_endpoint(swagger)
    check_operations(swagger)
    check_refs(swagger)
    check_auth_wiring(parsed[PROPERTIES], swagger)
    check_examples(swagger, parsed)

    report()
    return 1 if failures else 0


def report() -> None:
    if failures:
        print(f"{len(failures)} problem(s):", file=sys.stderr)
        for message in failures:
            print(f"  {message}", file=sys.stderr)
    else:
        print(f"connector definition OK ({len(json_files())} JSON files checked)")


if __name__ == "__main__":
    raise SystemExit(main())
