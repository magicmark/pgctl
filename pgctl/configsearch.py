#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""stolen from aactivator"""
# TODO: package and share
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

log = logging.getLogger(__name__)


def get_filesystem_id(path):
    return os.stat(path).st_dev


def search_parent_directories(path='.'):
    from os.path import abspath, dirname
    path = abspath(path)
    original_fs_id = fs_id = get_filesystem_id(path)
    previous_path = None

    while original_fs_id == fs_id and path != previous_path:
        yield path
        previous_path = path
        path = dirname(path)
        fs_id = get_filesystem_id(path)


def glob(pattern):
    from glob import glob
    for fname in sorted(glob(pattern)):
        yield fname


def parentglob(pattern, path='.'):
    from os.path import join
    for parent_dir in search_parent_directories(path):
        for found in glob(join(parent_dir, pattern)):
            yield found


def main():
    from sys import argv
    for pattern in argv[1:]:
        for found in parentglob(pattern):
            print(found)


if __name__ == '__main__':
    exit(main())
