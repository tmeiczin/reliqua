from .status_codes import HTTP


class Swagger(object):

    def __init__(self, url, swagger_file, path):
        self.url = url
        self.swagger_file = self.url + "/" + swagger_file
        self.path = path

    def on_get(self, req, resp, filename="index.html"):
        resp.status = HTTP(200)
        resp.content_type = "text/html"

        with open(self.path + "/" + filename, "r") as f:
            data = f.read()

        data = data.replace("<swagger_json_url>", self.swagger_file)
        data = data.replace("<swagger_url>", self.url)

        resp.body = data
