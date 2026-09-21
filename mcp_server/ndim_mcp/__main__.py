"""Entry point: python -m ndim_mcp [--transport stdio|streamable-http]."""
import argparse
import logging
import sys

from .server import create_server


def main(argv=None):
    parser = argparse.ArgumentParser(prog='ndim-mcp', description='NDIM engine MCP server')
    parser.add_argument('--transport', choices=('stdio', 'streamable-http'), default='stdio')
    parser.add_argument('--host', default='127.0.0.1', help='streamable-http only; there is no authentication, keep it local')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args(argv)
    # stdout carries the MCP protocol on stdio; every log line must go to stderr.
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s %(name)s %(message)s')
    create_server(host=args.host, port=args.port).run(transport=args.transport)


if __name__ == '__main__':
    main()
