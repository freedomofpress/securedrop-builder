#!/usr/bin/env python3

# This will update the index.html under /simple/
import os


STARTHTML = """<!DOCTYPE html>
<html>
  <head>
    <title>Simple index</title>
  </head>
  <body>
"""
ENDHTML = """  </body>
</html>
"""


names = os.listdir("./simple/")
names.sort()
with open("./simple/index.html", "w") as fobj:
    fobj.write(STARTHTML)

    for name in names:
        # We don't need index.html in the index itself.
        if name == "index.html":
            continue
        url = '    <a href="/simple/{0}/">{0}</a>\n'.format(name)
        fobj.write(url)

    fobj.write(ENDHTML)
