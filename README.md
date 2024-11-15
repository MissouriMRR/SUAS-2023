# SUAS-2025

Missouri S&amp;T Multirotor Drone Design Team's code for the Association for Unmanned Vehicle Systems International's 2025 Student Unmanned Aerial Systems Competition (AUVSI SUAS 2025) hosted by Robonation

## Table of contents

- [Installations](#installations)
    - [Git](#git)
    - [GitHub Credential Manager](#github-credential-manager)
    - [Python and Pip](#python-and-pip)
    - [Getting the Repo](#getting-the-repo)
    - [Pre-commit](#pre-commit)
    - [Poetry](#poetry)
- [Development](#development)
    - [Branches](#branches)
    - [Commits and Contributing](#commits-and-contributing)
    - [Pull Requests](#pull-requests)
- [License](#license)

## Installations

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

Go to your documents folder and clone the repo with `git clone https://github.com/MissouriMRR/SUAS-2025.git`

### Pre-commit

Pre-commit is a git hook that will check your code to make sure it is up to our standards before you make a commit. It is required that your code passes our pre-commit checks to be merged into the develop branch. That being said, when working on your own branch, you can add the `--no-verify` flag to your git commit command in order to bypass pre-commit. Just make sure you successfully run pre-commit before you submit a pull request.

To install it, run the command `pip3 install pre-commit`. You will need to restart your system for this to take effect.

Once you have restarted, open a terminal and navigate to the repo.

Run the command `pre-commit install`.

You can test that this worked by running `pre-commit run`.

### Poetry

Poetry is a virtual shell that allows use to ensure you have all packages and tools set up for the repo correctly.

To install, run `pip3 install poetry`.

Open a terminal and navigate to the repo. Run the command `poetry install`. This will install all dependencies needed.

Run `poetry shell` to open a virtual shell environment.


## Development

### Branches

For each issue that you work on, you should create a new branch.

1. Run `git checkout -b feature/issue` to create a new branch. Replace issue with something descriptive.
2. Run `git push` to push your new branch to the repo.

### Commits and Contributing

***Note: Never directly commit to the `develop` branch! Make sure you are on a seperate branch.***

1. Once you are on a new branch, you can start writing new code.
2. Add files to your next commit using `git add <filename>`.
3. Run `git commit -m "Description of changes"` to commit your code to the repo.
4. You should test your code in a poetry shell. Open the shell using `poetry shell`.
5. When you attempt to commit, pre-commit should automatically check your code to make sure it is up to our standards. If you fail the tests, go back and change what it requests. You can also use the command `pre-commit run` to run pre-commit checks without commiting.
6. Alternatively, if you just want to quickly push code to the repo, you can add the `--no-verify` flag to your git commit command to skip running pre-commit. For example, `git commit --no-verify -m "Updated readme"`. *Note, however, that your code will not be allowed to be merged into develop until it passes our pre-commit checks, so make sure you go back and fix any issues before submitting a pull request*.
7. Use `git push` to push your commits to the remote repo.


### Pull Requests

Once you have code that you think is ready to merge into develop, you can submit a pull request.

A template for your pull requests is available at `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`

Your pull request should describe what changes you made and what issue you solved.

On the sidebar, request a review from your sublead, assign yourself, apply appropriate labels, add to your subteam's project board, and tie to an issue.

## License

We adopt the MIT License for our projects. Please read the [LICENSE](LICENSE) file for more info
