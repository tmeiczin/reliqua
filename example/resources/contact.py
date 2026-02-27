"""
Contact resource — demonstrates multipart form data handling.

Features shown:
- Form parameters (in=form) for multipart file/field uploads
- Required form fields with validation
- no_auth = True for public endpoints
- :accepts form: content type declaration

Copyright 2016-2024.
"""

from reliqua.resources.base import Resource

# ---------------------------------------------------------------------------
# In-memory store for submitted messages
# ---------------------------------------------------------------------------

messages = []


class Contact(Resource):
    """Contact form submission.

    Demonstrates:
    - Multipart form data (in=form) — used for HTML form submissions
      and file uploads. The ProcessParams middleware automatically
      extracts form fields into req.params.
    - Public endpoint via no_auth = True
    - :accepts form: tells OpenAPI this endpoint expects multipart/form-data
    """

    __routes__ = {"/contact": {}}

    __tags__ = ["contact"]

    # Public — no authentication required
    no_auth = True

    def on_post(self, req, resp):
        """
        Submit a contact message.

        Accepts multipart form data with subject, email, and message fields.
        All fields are required.

        :param str subject:     [in=form required] Message subject
        :param str email:       [in=form required] Sender email address
        :param str message:     [in=form required] Message body

        :response 200:          Message was submitted
        :response 400:          Missing required fields

        :accepts form:
        :return json:
        """
        p = req.params
        entry = {
            "subject": p.get("subject"),
            "email": p.get("email"),
            "message": p.get("message"),
        }
        messages.append(entry)
        resp.media = {"success": True, "id": len(messages) - 1}

    def on_get(self, _req, resp):
        """
        List submitted messages.

        Returns all previously submitted contact messages.

        :response 200:          Messages were retrieved

        :return json:
        """
        resp.media = {"messages": messages, "count": len(messages)}
