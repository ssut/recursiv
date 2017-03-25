import argparse
import logging

from .client import RecursivClient
from .version import VERSION


def main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='Recursiv',
        description='Recursive autoindex downloader'
    )
    parser.add_argument('url',
                        metavar='URL',
                        help='URL to download')
    parser.add_argument('-o', '--output-dir',
                        type=str,
                        nargs='?',
                        default='.',
                        help='Path to download')
    parser.add_argument('-c', '--connections',
                        type=int,
                        nargs='?',
                        default=5,
                        help='Number of concurrent downloads')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='debug mode')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + VERSION)
    return parser


def main():
    parser = main_parser()
    args = parser.parse_args()
    logger = logging.getLogger('recursiv')
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    level = logging.DEBUG if args.debug else logging.INFO
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)

    recursiv = RecursivClient(
        index_url=args.url,
        output_dir=args.output_dir,
        num_connections=args.connections
    )
    recursiv.run()


if __name__ == '__main__':
    main()
