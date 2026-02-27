"""
Example resource modules.

Each module demonstrates different Reliqua features:

- users.py    — CRUD with multiple routes, suffixes, body/query/path params,
                typed lists, component schemas, role-based __auth__, get_params()
- servers.py  — Multiple routes per resource, path param type coercion,
                query list params, operator parsing
- contact.py  — Multipart form parameters (in=form), no_auth public resource
- files.py    — Binary and gzip streaming responses, content type negotiation
- health.py   — Minimal public endpoint, resource attributes, app config access,
                status code helpers, accepts/return content types

Copyright 2016-2024.
"""
