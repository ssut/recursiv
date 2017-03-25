import argparse
import logging

from .version import VERSION


def main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='Recursiv',
        description='Recursive autoindex downloader'
    )
    parser.add_argument('url',
                        metavar='URL',
                        help='URL to download')
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
    level = logging.DEBUG if args.verbose else logging.INFO
    handler.setLevel(level)
    logger.setLevel('level')


if __name__ == '__main__':
    main()
