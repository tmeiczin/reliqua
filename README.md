This is sample template to create a quick Python Falcon API application. It uses a schema defined in the resource for the route path and swagger documentation. The base application will handle creating the routes and documentation automatically at runtime.

You define a resource, then add a schema based on the OpenAPI specification.

```python

from reliqua.resources.base import Resource
from reliqua import status_codes as status


class User(Resource):

    __routes__ = [
        '/users/{id}',
    ]

    phone = phone

    def on_get(self, req, resp, id=None):
        """
        Retrieve a user. This value
        is awesome

        :param str id:       [in_path, required] User ID
        :param str email:    [in_query] User Email
        :param str phone:    [in_query, enum] Phone Numbers

        :response 200:
        :response 400:

        :return json:
        """
        try:
            resp.media = users[int(id)]
        except IndexError:
            resp.status = status.HTTP_404

    def on_delete(self, req, resp, id=None):
        try:
            users.pop(int(id))
            resp.media = {'success': True}
        except IndexError
            resp.status = status.HTTP_400
```

This will create the /users/{id} endpoint and swagger documentation. The swagger documentation and swagger.json will be dynamically generate at application startup. The swagger ui will be available at:

```
http://<api-url>/docs/
```

and the swagger.json file located at:

```
http://<api-url>/docs/swagger.json
```

To create an application, you import the application template.

```python
from reliqua.app import Application

    
app = Application(
    bind='0.0.0.0:8000',
    proxy_api_url = 'http://example.com/api',
    workers=1,
    resource_path='/var/www/html/resources'
)
app.run()
```

```
Where:

bind:           Address and port to listen for requests. [host:port]
proxy_api_url:  The URL to the API when being used with a proxy, like nginx. If not supplied,
                then the bind address is used.
workers:        Number of worker threads to start.
resource_path:  This is where your python resource files are located.
```

Refer to the example application for more examples. You can install the library and example application

```
python setup.py install
```

You can execute the example application

```
$ reliqua-example 
```

From here the swagger-ui will be available at

````
http://localhost:8000/docs/
````
