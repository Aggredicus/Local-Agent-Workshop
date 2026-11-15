"""Offline JSON Schema checks for an already metadata-validated registry.

Development-only dependencies are imported on demand. References resolve only to
registered, preloaded repository schemas; evaluation never retrieves a URL/file.
"""
from __future__ import annotations

import json
from pathlib import Path


def _reject_constant(value):
    raise ValueError('Non-finite literals are not valid JSON')


def load_document(path: Path):
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=_reject_constant)


def check_content(root: Path, registry: dict) -> tuple[dict, list[str]]:
    coverage = {'schemas_checked': 0, 'examples_checked': 0, 'references_checked': 0, 'network_retrieval': False, 'available': False}
    errors: list[str] = []
    try:
        from jsonschema import Draft202012Validator, validators
        from jsonschema.exceptions import SchemaError, ValidationError
        from referencing import Registry, Resource
        from referencing.exceptions import NoSuchResource
        from referencing.jsonschema import DRAFT202012
    except ImportError:
        return coverage, ['Schema content checks require development dependencies; install the project with .[dev].']
    coverage['available'] = True

    def deny_retrieval(uri):
        raise NoSuchResource(uri)

    resources = Registry(retrieve=deny_retrieval)
    schemas = []
    seen_ids: set[str] = set()
    for record in registry['schemas']:
        if record['status'] == 'planned':
            continue
        label = record['schema_id']
        path = (root / record['path']).resolve()
        coverage['schemas_checked'] += 1
        try:
            schema = load_document(path)
            cls = validators.validator_for(schema, default=None) if isinstance(schema, dict) and '$schema' in schema else Draft202012Validator
            if cls is None:
                errors.append(f'{label}: unsupported declared JSON Schema dialect')
                continue
            cls.check_schema(schema)
            resource = Resource.from_contents(schema, default_specification=DRAFT202012)
            schema_id = resource.id()
            if schema_id is not None:
                if schema_id in seen_ids:
                    errors.append(f'{label}: duplicate schema $id')
                    continue
                seen_ids.add(schema_id)
                resources = resources.with_resource(schema_id, resource)
            resources = resources.with_resource(path.as_uri(), resource)
            schemas.append((record, path, cls, resource))
        except (OSError, UnicodeError, ValueError, TypeError, SchemaError, RecursionError):
            errors.append(f'{label}: schema is unreadable JSON or an invalid JSON Schema')

    try:
        resources = resources.crawl()
    except Exception:
        errors.append('Registered schema resource identifiers could not be resolved offline')
        return coverage, errors
    for record, path, cls, resource in schemas:
        try:
            pending = [(resource, resources.resolver(path.as_uri()).in_subresource(resource))]
            while pending:
                current, resolver = pending.pop()
                if isinstance(current.contents, dict):
                    for keyword in ('$ref', '$dynamicRef', '$recursiveRef'):
                        if keyword in current.contents:
                            coverage['references_checked'] += 1
                            resolver.lookup(current.contents[keyword])
                pending.extend((child, resolver.in_subresource(child)) for child in current.subresources())
        except Exception:
            errors.append(f"{record['schema_id']}: schema reference is unavailable in the registered offline resources")
            continue
        # A file-URI wrapper supplies the local base for relative refs while all
        # resources are preloaded. No network or arbitrary file retrieval occurs.
        validator = cls({'$ref': path.as_uri()}, registry=resources)
        for example in record['example_paths']:
            coverage['examples_checked'] += 1
            label = record['schema_id']
            try:
                instance = load_document(root / example)
            except (OSError, UnicodeError, ValueError, RecursionError):
                errors.append(f'{label}: example is unreadable JSON')
                continue
            try:
                validator.validate(instance)
            except ValidationError as error:
                # Do not print the instance, values, or a library error message
                # which can contain credential-bearing example data.
                keyword = error.validator or 'false schema'
                errors.append(f'{label}: example violates the JSON Schema {keyword} constraint')
            except Exception:
                errors.append(f'{label}: example schema references could not be resolved or evaluated offline')
    return coverage, errors
