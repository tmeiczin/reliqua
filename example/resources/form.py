"""
Reliqua Framework.

Copyright 2016-2024.
"""

from reliqua.exceptions import HTTPBadRequest
from reliqua.resources.base import Resource


class Contact(Resource):
    """User resource."""

    __routes__ = {
        "/contact": {},
    }

    __tags__ = [
        "contact",
    ]

    no_auth = True

    def on_post(self, req, resp):
        """
        Send contact message.

        :param str subject:      [in=form required=True]     Subject
        :param str email:        [in=form required=True]     Sender email
        :param str message:      [in=form required=True]     Message contents

        :accepts form:
        :return json:
        """
        p = req.params
        if p.get("subject"):
            resp.media = {"success": True}
        else:
            raise HTTPBadRequest
