#!/usr/bin/env python3

# To create the project directory structure from a given requirements.txt file
# Usage: ./scripts/createdirs.py ~/projects/myproject/requirements.txt

import os
import sys
import json
import shutil

if len(sys.argv) != 2:
    print("Missing path to the requirements.txt.")
    sys.exit(1)

DATA = open("./templates/project-index.html").read()

with open(sys.argv[1]) as fobj:
    lines = fobj.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        words = line.split("==")
        assert len(words) == 2
        name = words[0]
        pathname = os.path.join("./simple/", name)
        os.makedirs(pathname, exist_ok=True)
        print("Project {0}".format(name))
        # Now make sure that we have an index.html there.
        project_index = os.path.join(pathname, "index.html")
        if not os.path.exists(project_index):
            with open(project_index, "w") as fobj:
                newdata = DATA.replace("PROJECT", name)
                fobj.write(newdata)
