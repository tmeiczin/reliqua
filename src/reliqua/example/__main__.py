import argparse
import os
import sys
from multiprocessing import cpu_count

from reliqua import Application, load_config


def main():
    bind_address = '127.0.0.01'
    bind_port = 8000
    proxy_api_url = None
    workers = (cpu_count() * 2) + 1
    parser = argparse.ArgumentParser()
    resource_path = os.path.abspath(os.path.dirname(
        sys.modules[__name__].__file__)) + '/resources'

    parser.add_argument('--address', help='API bind address to listen for requests', default=bind_address)
    parser.add_argument('--port', help='Bind port to listen for requests', default=bind_port)
    parser.add_argument('--proxy_api_url', help='URL to API for Swagger', default=proxy_api_url)
    parser.add_argument('--resource-path', help='Path to API resource modules', default=resource_path)
    parser.add_argument('--workers', help='Number of worker threads', default=workers)
    parser.add_argument('--config', help='Configuration file', default=None)

    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
        for k, v in config.iteritems():
            if getattr(args, k, None):
                setattr(args, k, v)

    app = Application(
        bind='%s:%s' % (args.address, args.port),
        workers=args.workers,
        resource_path=args.resource_path,
        proxy_api_url=args.proxy_api_url,
        version='1.0.0',
        desc='Example API',
        title='Reliqua Example'
    )
    app.run()


if __name__ == '__main__':
    main()
