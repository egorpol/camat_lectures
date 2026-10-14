# Setup on Jupyter4NFDI

[Jupyter4NFDI](https://hub.nfdi-jupyter.de) is a JupyterLab service for research and teaching. You sign in with your university account through Helmholtz AAI; nothing has to be installed on your computer.

## First login

1. Open <https://hub.nfdi-jupyter.de> and sign in with Helmholtz AAI (choose your university).
2. Start JupyterLab on **JSC-Cloud**.
3. Check the Python version: open a notebook and run `import sys; print(sys.version)`. You need Python 3.11 or later.

## Get the session notebooks

1. Download the notebook from the session page (section *Notebooks*).
2. In JupyterLab, click the **Upload** button (arrow icon) above the file browser and choose the file.
3. Open the notebook and run the first cell. It installs what the notebook needs (`%pip install ...`).
4. Run the next cells. A rendered score is the sign that everything works.

Files in your home folder (`/home/jovyan`) are kept when the server stops; everything else is discarded. Installed packages may have to be installed again after a restart: just run the first cell again.

## If something goes wrong

Problems from the first session and their fixes will be collected here.
