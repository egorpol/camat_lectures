# Setup on Jupyter4NFDI

[Jupyter4NFDI](https://hub.nfdi-jupyter.de) is a JupyterLab service for research and teaching. You sign in with your university account through Helmholtz AAI; nothing has to be installed on your computer.

In session 1, everyone works here. From session 2 on, most of you work on [your own laptop](setup-laptop.md). If you only have a tablet, or the laptop setup does not work for you, you continue on Jupyter4NFDI: see [From session 2: the cloud route](#from-session-2-the-cloud-route).

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

## From session 2: the cloud route

The cloud route gives you the same packages as the laptop setup, in your browser: Python 3.12, Poppler (reads PDF pages), CAMAT and Verovio. You need your university account and a GitHub account. On a tablet, a keyboard helps.

| Step | What you get | What it is for |
|---|---|---|
| 1 | a GitHub account | shares your edition; signs you in to mei-friend |
| 2 | the seminar's JupyterLab | everything the notebooks need, already installed |
| 3 | the notebooks | a final check that everything works |
| 4 | mei-friend | the MEI editor in the browser, from session 3 on |

### 1. Create a GitHub account

Follow [step 1 of the laptop setup](setup-laptop.md#1-create-a-github-account).

**✓ Check:** you are logged in at <https://github.com> and see your username in the top right corner.

### 2. Start the seminar's JupyterLab

1. Open the seminar's workshop link. You get it in class.
2. Sign in as in session 1: Helmholtz AAI, then your university.
3. Start JupyterLab. The settings are already chosen for you; keep them. The start can take a few minutes.

JupyterLab opens as in session 1, but with the seminar's packages already installed. **Only the folder `work` is kept** when the server stops; everything outside it is reset at the next start. Keep all your seminar files in `work`.

**✓ Check:** the file browser on the left shows the folder `work`.

??? question "If it goes wrong"
    - **The start fails or takes longer than 15 minutes:** reload the page and start again. If it fails twice, tell the instructor; see also [If the workshop link does not work](#if-the-workshop-link-does-not-work).
    - **There is no folder `work`:** tell the instructor before you go on. Without it, your files would not be kept.

### 3. Get the notebooks and run the final check

1. In the file browser, double-click `work` to open it.
2. Open a new notebook there (*File → New → Notebook*, kernel **Python 3 (ipykernel)**), paste this into the first cell and run it:

    ```python
    import urllib.request
    urllib.request.urlretrieve("https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.py", "get_notebooks.py")
    %run get_notebooks.py
    ```

    The notebooks land in `work/camat_lectures/`, one folder per session. Save this small notebook as `get_notebooks.ipynb` and run it again before each session: it adds new notebooks and keeps the ones you already have.

3. Open `camat_lectures` → `02-building-an-edition` → `02_pdf_preparation.ipynb`.
4. Click into the first grey code cell and press ++shift+enter++, or click ▶ in the toolbar above the notebook. Repeat for each cell, until a cell prints `CAMAT: 0.2.8`. Stop there; the rest of the notebook is for class.

**✓ Check:** a cell prints `CAMAT: 0.2.8` and `pypdf: 6.10.0`, with no red error. You are ready.

??? question "If it goes wrong"
    - **`camat_lectures` appears outside `work`:** the small notebook was not in `work`. Delete both, open `work`, and repeat point 2.
    - **"Poppler's pdftoppm is missing" or "No module named camat":** this JupyterLab was not started from the workshop link. Open the workshop link again and start JupyterLab from there.

### 4. Try mei-friend

[mei-friend](https://mei-friend.mdw.ac.at/) is an editor for MEI files that runs in the browser. We use it from session 3 on.

1. Open [the Schumann file of the MEI Sample Collection in mei-friend](https://mei-friend.mdw.ac.at/?file=https://raw.githubusercontent.com/music-encoding/sample-encodings/e4a3c4dece588ae0bdb13e5cf956340dcd99b447/MEI_5.1/Music/Complete_examples/Schumann_Landmann_Op68_No10.mei&select=d1e338). The link selects one note.
2. The first time, a welcome box appears: click **Got it!**.
3. Click **Login** at the top left and sign in with your GitHub account. You need this from session 3 on, when you save your edition to GitHub.

**✓ Check:** the score appears on the left with one bass note in blue, and the code on the right highlights the line `<note xml:id="d1e338" pname="a" .../>`. It is the wrong note A3 from session 2, part 3.

### If the workshop link does not work

??? warning "Set up the seminar environment yourself (10–20 minutes)"
    Use this only if the instructor tells you to. It installs the same packages into your Jupyter4NFDI home folder, where they stay; you do it once.

    1. Start JupyterLab from <https://hub.nfdi-jupyter.de> on **JSC-Cloud**, as in session 1.
    2. Open a terminal (*File → New → Terminal*) and run these three commands one at a time. The first two take several minutes each:

        ```sh
        conda create -y -p ~/envs/seminar --override-channels -c conda-forge python=3.12 poppler ipykernel
        ~/envs/seminar/bin/python -m pip install "camat[validation,notebooks]==0.2.8" verovio==6.3.0 pypdf==6.10.0
        ~/envs/seminar/bin/python -m ipykernel install --user --name seminar --display-name "Python (seminar)" --env PATH "$HOME/envs/seminar/bin:$PATH"
        ```

    3. Reload the browser tab. Get the notebooks as in [Get the session notebooks](#get-the-session-notebooks) above; here your home folder is kept, so you do not need `work`.
    4. Open `02_pdf_preparation.ipynb`, choose *Kernel → Change Kernel… → Python (seminar)*, and run the cells until `CAMAT: 0.2.8`.

    In every seminar notebook from session 2 on, choose the kernel **Python (seminar)**. The environment uses about 1.3 GB of your storage.

## If something goes wrong

Problems from the first session and their fixes will be collected here.
