#!/usr/bin/env python3

# This script finds the currently available sources
# and wheels built by SecureDrop team and creates
# a list of URLs to download them from the s3.

import os

DEV_WHEELS_BUCKET_BASE_URL = "https://dev-bin.ops.securedrop.org/localwheels"
WHEELS_BUCKET_BASE_URL = os.environ.get(
    "WHEELS_BUCKET_BASE_URL", DEV_WHEELS_BUCKET_BASE_URL
)


with open("./sha256sums.txt") as fobj:
    lines = fobj.readlines()


def main():
    "Entry point for the command"
    filenames = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        words = line.split()
        if len(words) == 2:
            filenames.append(words[1])
        else:
            print("Wrong line: {0}".format(line))

    filenames = list(set(filenames))
    filenames.sort()
    for name in filenames:
        print("{0}/{1}".format(WHEELS_BUCKET_BASE_URL, name))
    
    print("Done! Now please follow the instructions in "
          "https://github.com/freedomofpress/securedrop-debian-packaging-guide/issues/6 "
          "to push these changes to the FPF PyPI index")


if __name__ == "__main__":
    main()
