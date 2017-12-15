This is sample template to create a quick Python Falcon API application. It uses a schema defined in the resource for the route path and swagger documentation. The base application will handle creating the routes and documentation automatically at runtime.

You define a resource, then add a schema based on the OpenAPI specification.

```python

from falcon_template.resources.base import Resource


class User(Resource):
    __schema__ = {
        '/users/{id}': {
            'get': {
                'description': 'retrieve users',
                'operationId': 'getUser',
                'tags': [
                    'users'
                ],
                'parameters': [
                    {
                        'name': 'id',
                        'in': 'path',
                        'description': 'User ID',
                        'required': True,
                        'type': 'string'
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'successful operation',
                        'examples': {
                            'application/json': {
                                'results': [
                                    {
                                        'username': 'fred',
                                        'email': 'fred@fake.com',
                                    }
                                ],
                                'success': True,
                            }
                        }
                    }
                }
            },
        }
    }

    def on_get(self, req, resp, id=None):
        resp.body = self.jsonify(users[int(id)])
        
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
from falcon_template.app import Application

    
app = Application(
    address='0.0.0.0',
    port=8000,
    workers=1,
    host='example.com,
    base_path='/api',
    resource_path='/var/www/html/resources'
)
app.run()
```

```
Where:

address:       ip address to listen to requests, 0.0.0.0 means any interface
port:          port to listen on
workers:       number of worker threads to start
host:          external hostname or ip address that is reachable from clients, used by swagger-ui
base_path:     the api base path for the api, used by swagger-ui
resource_path: this is where your python resource files are located
```

Refer to the example application for more examples. You can install the library and example application

```
python setup.py install
```

You can execute the example application

```
$ falcon-app 
```

From here the swagger-ui should be available at

````
http://localhost:8000/docs/
````
