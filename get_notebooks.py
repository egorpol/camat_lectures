"""Copy the seminar notebooks from GitHub into camat_lectures/, without git.

In a notebook cell on Jupyter4NFDI (or any JupyterLab):

    import urllib.request
    urllib.request.urlretrieve("https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.py", "get_notebooks.py")
    %run get_notebooks.py

or in a terminal: python get_notebooks.py

The notebooks land in camat_lectures/<session>/ below the current folder.
Run it again after each session to get the new ones. Notebooks you already
have are never overwritten, so your changes are safe; to get a fresh copy
of one, rename or delete yours and run the script again.
"""

import io
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath

REPO = "https://github.com/egorpol/camat_lectures"
ARCHIVE = "https://codeload.github.com/egorpol/camat_lectures/tar.gz/refs/heads/main"
DEST = Path("camat_lectures")


def download():
    request = urllib.request.Request(ARCHIVE, headers={"User-Agent": "camat-lectures-get-notebooks"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.URLError as exc:
        sys.exit(f"Could not download the notebooks from {REPO}: {getattr(exc, 'reason', exc)}\n"
                 "Check the network, or download them from the session page and upload them.")


# Archive members look like camat_lectures-main/sessions/<session>/notebooks/<name>.ipynb.
def notebook_path(member):
    parts = PurePosixPath(member.name).parts
    if (member.isfile() and len(parts) == 5 and parts[1] == "sessions" and parts[3] == "notebooks"
            and parts[4].endswith(".ipynb") and ".." not in parts):
        return DEST / parts[2] / parts[4]
    return None


def main():
    print(f"Downloading the notebooks from {REPO} ...")
    new, kept = [], []
    with tarfile.open(fileobj=io.BytesIO(download()), mode="r:gz") as tar:
        for member in tar.getmembers():
            target = notebook_path(member)
            if target is None:
                continue
            if target.exists():
                kept.append(target)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
            new.append(target)
    for label, paths in (("New", new), ("Already there, kept as they are", kept)):
        if paths:
            print(f"{label}:")
            for path in sorted(paths):
                print(f"  {path}")
    if not new and not kept:
        sys.exit("The download has no notebooks in it. Please tell the instructor.")
    print(f"Open them from the file browser: {DEST.resolve()}")


if __name__ == "__main__":
    main()
