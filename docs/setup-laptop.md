# Setup on your laptop

From session 2 on, we work on your own laptop. You open the notebooks in **VS Code**, run them with **Python**, keep the history of your edition with **Git**, and share it on **GitHub**. We set this up together in class, step by step.

**How to use this page**

- Choose your system in the first tab (Windows, macOS or Linux). All tabs on the page then switch to it.
- Do the steps in order. Each step ends with a **✓ Check**. Only go on when you see what the check describes.
- If a check fails, open **If it goes wrong** below it. If that does not help, raise your hand. Many problems are the same for several people, so asking early saves everyone time.
- You need about 2 GB of free disk space and the password of your laptop (installers ask for it).

!!! tip "Optional: download the installers at home"
    The university Wi-Fi gets slow when everyone downloads at once. If you can, download the installers for your system before class (links in steps 2, 3 and 5) and keep them in your Downloads folder.

| Step | What you get | What it is for |
|---|---|---|
| 1 | a GitHub account | shares your edition; also signs you in to Copilot |
| 2 | VS Code | the editor for notebooks and MEI files |
| 3 | Miniforge | installs Python, the language our notebooks are written in |
| 4 | the `seminar` environment | Python, Poppler (reads PDF pages) and the seminar's packages |
| 5 | Git | keeps the history of your edition |
| 6 | VS Code connected to GitHub | lets VS Code send your work to GitHub, and switches on Copilot |
| 7 | the notebooks | a final check that everything works together |

## 1. Create a GitHub account

1. Open <https://github.com/signup> in your browser.
2. Enter your e-mail address, a password and a username. Your username appears in your edition's web address, so choose something you are happy to show, for example your name.
3. GitHub sends a code to your e-mail address. Enter it to verify the account.

GitHub may also ask you to turn on **two-factor authentication** (a second check when you log in, with an app on your phone). You can do that now or later; GitHub tells you the deadline.

**✓ Check:** you are logged in at <https://github.com> and see your username in the top right corner.

??? question "If it goes wrong"
    - **No e-mail arrives:** look in your spam folder. University addresses sometimes delay mail by several minutes; you can continue with step 2 and come back.
    - **The username is taken:** add a number or your initials.

## 2. Install VS Code

=== "Windows"

    1. Open <https://code.visualstudio.com/download> and click the big **Windows** button. This downloads the *User Installer*.
    2. Open the downloaded file (`VSCodeUserSetup-…exe`) from your Downloads folder.
    3. Accept the agreement and keep the default options. On the page *Select Additional Tasks*, leave **Add to PATH** ticked.
    4. At the end, leave **Launch Visual Studio Code** ticked and click **Finish**.

=== "macOS"

    1. Open <https://code.visualstudio.com/download> and click the big **Mac** button. This downloads a `.zip` file.
    2. Open your Downloads folder and double-click the `.zip`. It unpacks into **Visual Studio Code**.
    3. Drag **Visual Studio Code** into your **Applications** folder.
    4. Open it from Applications. If macOS asks whether you want to open an app downloaded from the internet, click **Open**.

=== "Linux"

    1. Open <https://code.visualstudio.com/download>.
    2. Ubuntu or Debian: download the **.deb** file, then run in a terminal:

        ```sh
        sudo apt install ~/Downloads/code_*.deb
        ```

        Fedora: download the **.rpm** file and run `sudo dnf install ~/Downloads/code-*.rpm`.

    3. Start **Visual Studio Code** from your applications menu.

Now add the two extensions we need:

1. In VS Code, click the **Extensions** icon in the bar on the left (four small squares), or press ++ctrl+shift+x++ (macOS: ++cmd+shift+x++).
2. Type `Python` in the search field. Click **Install** on **Python** by Microsoft.
3. Type `Jupyter` and install **Jupyter** by Microsoft.

**✓ Check:** in the Extensions view, both **Python** and **Jupyter** show a gear icon instead of an **Install** button.

??? question "If it goes wrong"
    - **Windows shows a blue "Windows protected your PC" box:** click **More info**, then **Run anyway**. Do this only for installers you downloaded from the links on this page.
    - **macOS says the app is damaged or cannot be opened:** make sure you moved it to Applications first, then right-click it and choose **Open**.
    - **Several extensions are called "Python":** take the one by **Microsoft** with the blue tick.

## 3. Install Miniforge

Miniforge installs Python, and it can also install programs that are not written in Python. We need one of those: **Poppler**, which reads PDF pages.

=== "Windows"

    1. Download the installer: <https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe>
    2. Open the downloaded file. Click **Next**, **I Agree**, choose **Just Me**, keep the suggested folder, and keep the default ticks on the last page. Click **Install**, then **Finish**.
    3. Open the **Start** menu, type `Miniforge Prompt` and open it. A black window appears. From now on, **all commands go into this window**, not into PowerShell or the ordinary Command Prompt.

    To paste a command into Miniforge Prompt, right-click in the window or press ++ctrl+v++. Then press ++enter++.

=== "macOS"

    1. Open **Terminal**: press ++cmd+space++, type `Terminal` and press ++enter++.
    2. Copy this line, paste it into Terminal with ++cmd+v++ and press ++enter++. It downloads the right installer for your Mac:

        ```sh
        curl -fsSLO "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
        ```

    3. Start the installer:

        ```sh
        bash Miniforge3-$(uname)-$(uname -m).sh
        ```

    4. Press ++enter++ to read the licence, then ++space++ until its end, and type `yes`. Press ++enter++ to keep the suggested location. When it asks whether to initialise (*"conda init"*), type `yes`.
    5. **Close Terminal completely** (++cmd+q++) and open it again. From now on, **all commands go into Terminal**.

=== "Linux"

    1. Open a terminal.
    2. Download and start the installer:

        ```sh
        curl -fsSLO "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
        bash Miniforge3-$(uname)-$(uname -m).sh
        ```

    3. Press ++enter++ to read the licence, then ++space++ until its end, and type `yes`. Press ++enter++ to keep the suggested location. When it asks whether to initialise (*"conda init"*), type `yes`.
    4. **Close the terminal** and open a new one. From now on, **all commands go into this terminal**.

Type this command and press ++enter++:

```sh
conda --version
```

**✓ Check:** it prints `conda` and a version number, for example `conda 25.9.1`. On Windows this happens in **Miniforge Prompt**.

??? question "If it goes wrong"
    - **Windows: "'conda' is not recognized":** you are in PowerShell or the ordinary Command Prompt. Open **Miniforge Prompt** from the Start menu instead.
    - **macOS/Linux: "conda: command not found":** close the terminal completely and open a new one. If it still fails, run `~/miniforge3/bin/conda init`, then close and reopen the terminal.
    - **macOS: `curl` prints nothing and no file appears:** check the Wi-Fi, then run the `curl` line again.

## 4. Create the seminar environment

An **environment** is a separate Python installation for one project. Ours is called `seminar`. Run these commands one at a time, in the same window as in step 3. Wait until each one has finished, that is, until you can type again.

1. Create the environment with Python and Poppler. This takes a few minutes:

    ```sh
    conda create -y -n seminar python=3.12 poppler
    ```

2. Switch to it:

    ```sh
    conda activate seminar
    ```

    The start of the line changes from `(base)` to `(seminar)`.

3. Install the seminar's packages: CAMAT, Verovio and their helpers. This downloads about 800 MB and can take 5–15 minutes. You can start step 5 in the meantime.

    ```sh
    pip install "camat[validation,notebooks]==0.2.8" verovio==6.3.0 pypdf==6.10.0
    ```

4. Check that everything is there:

    ```sh
    python --version
    pdftoppm -v
    python -c "import camat, verovio; print('ready')"
    ```

**✓ Check:** `Python 3.12…`, a line beginning `pdftoppm version`, and `ready`.

??? question "If it goes wrong"
    - **The line still starts with `(base)`:** run `conda activate seminar` again. You need this every time you open a new window.
    - **`pip install` stops with a network or timeout error:** run the same `pip install` line again. Packages that already arrived are not downloaded twice.
    - **"No module named camat":** the `pip install` line did not finish. Look for `Successfully installed` at its end; if it is missing, run it again inside `(seminar)`.

## 5. Install Git

=== "Windows"

    1. Open <https://git-scm.com/downloads/win> and click **Click here to download** (the 64-bit *Git for Windows Setup*).
    2. Open the downloaded file. Click **Next** on every page, with one exception: on the page *Choosing the default editor used by Git*, pick **Use Visual Studio Code as Git's default editor**.
    3. Click **Install**, then **Finish**.
    4. Wait until the `pip install` from step 4 has finished. Then **close Miniforge Prompt and open it again**, so that it finds Git.

=== "macOS"

    1. If Terminal is still busy with step 4, open a second window with ++cmd+n++.
    2. Type `git --version` and press ++enter++.
    3. If Git is missing, macOS asks to install the *command line developer tools*. Click **Install** and accept the licence. This takes 5–15 minutes.

=== "Linux"

    If the terminal is still busy with step 4, open a second one. Then run, for Ubuntu or Debian, `sudo apt install git`; for Fedora, `sudo dnf install git`.

Now tell Git who you are, in a window that is not busy. Every change you record carries this name and e-mail address. Use the e-mail address of your GitHub account:

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.org"
git config --global --list
```

If you prefer not to show your address, GitHub gives you a private one under **Settings → Emails** (it ends in `@users.noreply.github.com`). Use that one instead.

**✓ Check:** `git --version` prints `git version 2.…`, and the last command lists your `user.name` and `user.email`.

??? question "If it goes wrong"
    - **Windows: "'git' is not recognized":** close Miniforge Prompt and open it again. If that does not help, restart the laptop.
    - **A typo in your name or address:** run the `git config` line again with the right value. It replaces the old one.

## 6. Connect VS Code to GitHub and Copilot

1. In VS Code, click the **Accounts** icon (a person) at the bottom of the bar on the left.
2. Choose the entry that offers to **sign in with GitHub**. Your browser opens; log in to GitHub and click **Authorize**. Allow the browser to go back to VS Code.
3. Open the chat with **View → Chat**. If VS Code asks you to set up Copilot, choose the **free** plan.
4. Try it: copy this question into the chat and send it.

    > What does `<note pname="f" oct="3" dur="4" dots="1"/>` mean?

**✓ Check:** the Accounts icon shows your GitHub username, and the answer mentions F3 and a dotted quarter note.

Copilot sends whatever you type or attach in the chat to GitHub's servers. Do not paste personal data into it.

??? question "If it goes wrong"
    - **The browser does not return to VS Code:** go back to VS Code yourself; it usually shows a box where you can paste the code from the browser.
    - **Copilot says you have no access:** check that you signed in with the same GitHub account as in step 1, then try **View → Chat** again.

## 7. Get the notebooks and run the final check

1. In Miniforge Prompt (Windows) or Terminal (macOS, Linux), make a folder for the seminar and download the notebooks into it:

    ```sh
    conda activate seminar
    mkdir seminar-work
    cd seminar-work
    python -c "import urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/egorpol/camat_lectures/main/get_notebooks.py', 'get_notebooks.py')"
    python get_notebooks.py
    ```

    The folder is in your home folder (Windows: `C:\Users\<your name>\seminar-work`). The notebooks land in `seminar-work/camat_lectures/`, one folder per session. Before each session, run `python get_notebooks.py` there again: it adds new notebooks and keeps the ones you already have.

2. In VS Code: **File → Open Folder…**, choose `seminar-work`, and confirm that you trust the folder.
3. In the file list on the left, open `camat_lectures` → `02-building-an-edition` → `02_pdf_preparation.ipynb`.
4. Click **Select Kernel** (top right), then **Python Environments…**, then **seminar**.
5. Click into the first grey code cell and press ++shift+enter++. Repeat for each cell, until a cell prints `CAMAT: 0.2.8`. Stop there; the rest of the notebook is for class.

**✓ Check:** a cell prints `CAMAT: 0.2.8` and `pypdf: 6.10.0`, with no red error. You are ready.

??? question "If it goes wrong"
    - **`seminar` is not in the kernel list:** open the Command Palette (++ctrl+shift+p++, macOS: ++cmd+shift+p++), run **Developer: Reload Window**, and try again. If it is still missing, choose **Select Another Kernel… → Python Environments… → Enter interpreter path** and type `C:\Users\<your name>\miniforge3\envs\seminar\python.exe` (Windows) or `~/miniforge3/envs/seminar/bin/python` (macOS, Linux).
    - **VS Code offers to install `ipykernel`:** click **Install**.
    - **"Poppler's pdftoppm is missing":** the notebook uses another Python. Select the **seminar** kernel as in point 4.

[mei-friend](https://mei-friend.mdw.ac.at/), the MEI editor we also use, runs in the browser (Chrome, Firefox or Edge) and needs no installation.
