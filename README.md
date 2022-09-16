# SUAS-2023
Missouri S&amp;T Multirotor Robot Design Team's code for the Association for Unmanned Vehicle Systems International's 2023 Student Unmanned Aerial Systems Competition (AUVSI SUAS 2023)

## Getting Started

*Note: It is recommended that you develop for this repository on Ubuntu 22.xx . All steps from this point on will assume you are on Ubuntu.*

This guide will walk you through the process of getting set up with the repo and the tools you will need for development.

### Git

Make sure you have git installed with `git --version`. If you do not, you can install it with `sudo apt-get install git`.

### GitHub Credential Manager

GitHub handles credentials in a way that can be confusing to use at the command line. This can be remedied by using GitHub CLI. GitHub CLI will store your Git credentials for HTTPS Git operations.

First, install `curl` with `sudo apt-get install curl`.

Then, run the command (yes this is one command):

```
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

Run the command `gh auth login` and follow the prompts. For options, choose `GitHub.com`, `HTTPS`, `Yes`, `Login with a web browser`. Authorize the session in the web browser and your GitHub credentials will be saved.

### Python and Pip

Ubuntu 22 should come preinstalled with Python 3.10.4 . Check with `python3 --version`.

You will need to install pip with `sudo apt-get install python3-pip`. Pip is used for managing Python packages.

### Getting the Repo

Go to your documents folder and clone the repo with `git clone https://github.com/MissouriMRR/SUAS-2023.git`

### Pre-commit

Pre-commit is a git hook that will check your code to make sure it is up to our standards before you make a commit. It is required that your code passes our pre-commit checks to be merged into the develop branch.

To install it, run the command `pip3 install pre-commit`. You will need to restart your system for this to take effect.

Once you have restarted, open a terminal and navigate to the repo.

Run the command `pre-commit install`.

You can test that this worked by running `pre-commit run`.

### Poetry

Poetry is a virtual shell that allows use to ensure you have all packages and tools set up for the repo correctly.

To install, run `pip3 install poetry`.

Open a terminal and navigate to the repo. Run the command `poetry install`. This will install all dependencies needed.

Run `poetry shell` to open a virtual shell environment.
