#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Authors: liangzhibang@baidu.com
# Date: 2018-05-21

__author__ = "liangzhibang@baidu.com"
__date__ = '2018/5/21'

import sys
from urllib.parse import urlparse, ParseResult, urljoin

import requests

DEBUG = True


def getfullurl(url: "http", path: ParseResult):
    # baseurl = urlunparse((path.scheme, path.netloc, path.path, "", "", ""))
    return urljoin(path.geturl(), url)


def main():
    link = sys.argv[1]
    if 'http' not in link:
        print("link must be http scheme")
    scheme = urlparse(link)
    with open(scheme.path[scheme.path.rfind('/') + 1:], 'wb') as f:
        m3u8 = requests.get(link).text
        for line in m3u8.splitlines():
            if line.startswith("#"):
                continue
            if "http" not in line:
                line = getfullurl(line, scheme)
            f.write(requests.get(line).content)
            print("Download %s successed" % (line))


