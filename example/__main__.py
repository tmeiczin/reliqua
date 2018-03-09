import argparse
import configparser
import os
import sys
from multiprocessing import cpu_count

from falcon_template.app import Application


def _load_config(args):
    config = configparser.ConfigParser()
    config.sections()
    config.read(args.config)

    if 'config' not in config.keys():
        return args

    c_args = [x.lstrip('-') for x in sys.argv[1:] if x.startswith('-')]
    for k, v in config['config'].items():
        if k not in c_args:
            setattr(args, k, v)

    return args


def main():
    bind_address = '127.0.0.01'
    bind_port = 8000
    host = 'localhost'
    base_path = ''
    workers = (cpu_count() * 2) + 1
    parser = argparse.ArgumentParser()
    resource_path = os.path.dirname(
        sys.modules[__name__].__file__) + '/resources'

    parser.add_argument('--address', help='API bind address to listen for requests', default=bind_address)
    parser.add_argument('--port', help='Bind port to listen for requests', default=bind_port)
    parser.add_argument('--host', help='External hostname/ip for swagger API', default=host)
    parser.add_argument('--base-path', help='External API path for swagger', default=base_path)
    parser.add_argument('--resource-path', help='Path to API resource modules', default=resource_path)
    parser.add_argument('--workers', help='Number of worker threads', default=workers)
    parser.add_argument('--config', help='Configuration file', default=None)

    args = parser.parse_args()

    if args.config:
        _load_config(args)

    app = Application(
        address=args.address,
        port=args.port,
        workers=args.workers,
        host=args.host,
        base_path=args.base_path,
        resource_path=resource_path
    )
    app.run()
