"""
Reliqua Example Application.

A comprehensive example demonstrating all major features of the Reliqua framework:

- Resource auto-discovery and routing (single and multiple routes with suffixes)
- Docstring-driven OpenAPI 3.1 documentation generation
- Parameter types: query, path, body, and form parameters
- Type coercion: str, int, float, bool, list, list[int], list[str], object
- Parameter options: required, default, enum, min, max
- Response schemas with component references
- Content type negotiation (JSON, XML, YAML, text, binary, gzip)
- Authentication: BasicAuthentication, CookieAuthentication, MultiAuthentication
- Authorization: AccessResource with per-resource __auth__ role mapping
- Public resources with no_auth = True
- Custom resource attributes and app config passthrough
- Status codes and exception handling
- Operator parsing in query parameters (e.g., ?age__gt=25)

Copyright 2016-2024.
"""
