# Setup on Jupyter4NFDI

[Jupyter4NFDI](https://hub.nfdi-jupyter.de) is a JupyterLab service for research and teaching. You sign in with your university account through Helmholtz AAI; nothing has to be installed on your computer.

## First login

1. Open <https://hub.nfdi-jupyter.de> and sign in with Helmholtz AAI (choose your university).
2. Start JupyterLab on **JSC-Cloud**.
3. Check the Python version: open a notebook and run `import sys; print(sys.version)`. You need Python 3.10 or later.

## Get the session notebooks

1. In JupyterLab, open a new notebook (*File → New → Notebook*), paste this into the first cell and run it:

    ```python
    import urllib.request
    urllib.request.urlretrieve("https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.py", "get_notebooks.py")
    %run get_notebooks.py
    ```

    The notebooks of all sessions so far appear in the folder `camat_lectures/`, one subfolder per session. Save this small notebook (for example as `get_notebooks.ipynb`): you will run it again.

2. Open a session notebook and run its first cell. It installs what the notebook needs (`%pip install ...`).
3. Run the next cells. A rendered score is the sign that everything works.

After each session, run the cell again to get the new notebooks. Notebooks you already have are kept as they are, so your changes are safe. To start one over, rename or delete your copy and run the cell again.

**Or from a terminal.** If you prefer the command line, open a terminal in JupyterLab (*File → New → Terminal*) and run:

```sh
curl -fsSLO https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.sh
bash get_notebooks.sh
```

It does the same as the notebook cell: the notebooks land in `camat_lectures/`, and notebooks you already have are kept. Next time, `bash get_notebooks.sh` is enough. If the terminal says `curl: command not found`, use `wget -q` instead of `curl -fsSLO` in the first line.

If the cell cannot download anything, download the notebooks from the session page (section *Notebooks*) and upload them with the **Upload** button (arrow icon) above the file browser.

Files in your home folder (`/home/jovyan`) are kept when the server stops; everything else is discarded. Installed packages may have to be installed again after a restart: just run the first cell again.

## If something goes wrong

Problems from the first session and their fixes will be collected here.
