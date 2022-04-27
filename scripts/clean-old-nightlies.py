#!/usr/bin/env python3
"""
Clean up nightly packages that are older than 14 days

Example:
    ./clean-old-nightlies.py securedrop-dev-packages-lfs/workstation/buster-nightlies

"""
import argparse
import datetime
import pathlib
import re


DELETE_OLDER_THAN = 14
PATTERN = re.compile(r'-dev-(\d{8})-')


def main():
    parser = argparse.ArgumentParser(
        description="Cleans up old nighly packages"
    )
    parser.add_argument(
        "directory",
        type=pathlib.Path,
        help="Directory to clean up",
    )
    args = parser.parse_args()
    if not args.directory.is_dir():
        raise RuntimeError(f"Directory, {args.directory}, doesn't exist")
    cutoff = str(datetime.date.today() - datetime.timedelta(days=DELETE_OLDER_THAN)).replace('-', '')
    print(f'Deleting files older than {cutoff}')
    for deb in args.directory.glob('*.deb'):
        search = PATTERN.search(deb.name)
        if search:
            age = search.group(1)
            if age < cutoff:
                print(f'Deleting {deb.name}...')
                deb.unlink()


if __name__ == '__main__':
    main()
