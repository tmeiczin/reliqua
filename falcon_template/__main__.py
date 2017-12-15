import argparse
import configparser
import socket
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
    workers = (cpu_count() * 2) + 1
    host = socket.gethostname()
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', help='bind address', default='127.0.0.1')
    parser.add_argument('--port', help='bind port', default=8000)
    parser.add_argument('--host', help='api doc host', default='localhost')
    parser.add_argument('--base-path', help='api base path', default='')
    parser.add_argument('--workers', help='worker threads', default=workers)
    parser.add_argument('--config', help='config file', default=None)

    args = parser.parse_args()

    if args.config:
        _load_config(args)

    app = Application(
        address=args.address,
        port=args.port,
        workers=args.workers,
        host=args.host,
        base_path=args.base_path
    )
    app.run()
