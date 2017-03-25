from typing import Tuple

import lxml.html


def extract_links(body: str) -> Tuple[set, set]:
    html = lxml.html.fromstring(body)
    urls = set([url
                for url in html.xpath('//a/@href')
                if not url.startswith('../')])

    directories = set([url
                       for url in urls
                       if url.endswith('/')])
    files = urls - directories
    return directories, files
