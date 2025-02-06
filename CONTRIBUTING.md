# Contributing to our Ansible Vault Rotate CLI
We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the configuration
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with GitHub
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [CircleCI](https://circleci.com/product/), So All Code Changes Happen Through Pull Requests
Pull requests are the best way to propose changes to the codebase (we use [CircleCI](https://circleci.com/product/)). We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the tests pass.
5. Make sure your code and commit lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](https://opensource.org/licenses/MIT) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's issues
We use GitHub issues to track public bugs. Report a bug by opening a new issue, it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
    - Be specific!
    - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Commit Message Format

We have very precise rules over how our Git commit messages must be formatted.

This format leads to **easier to read commit history** and the ability to create automated releases with semantic-commit.

More information about conventional commit messages can be found [here](https://www.conventionalcommits.org/en/v1.0.0/#summary)

```text
<type>(<scope>): <short summary>
  │       │             │
  │       │             └─⫸ Summary in present tense. Not capitalized. No period at the end.
  │       │
  │       └─⫸ Commit Scope: This is usually a ticket number, if available
  │
  └─⫸ Commit Type: build|ci|docs|feat|feat!|fix|perf|refactor|test
```

The `<type>` and `<summary>` fields are mandatory, the `(<scope>)` field is optional.

Example: `feat(TPSDO-1337): added option for additional environment variables`

#### Release type per commit message

| Commit message           | Release type     |
|--------------------------|------------------|
| fix(scope): summary      | Patch Release    |
| feat(scope): summary     | Feature Release  |
| perf(scope): summary     | Breaking Release |
| feat(scope)!: summary    | Breaking Release |

In addition to the above shown combinations of type and summary, you can also trigger a breaking change with an extended summary by using the following commit message:

```text
feat(scope): summary

BREAKING CHANGE: extended summary for the breaking change section
```

:warning: The `BREAKING CHANGE` content must be part of the commit message body


## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## Developer Certificate of Origin
Every external contributor needs to sign commits with a valid DCO.

This is done by adding a Signed-off-by line to commit messages.

```
This is my commit message

Signed-off-by: Random J Developer <random@developer.example.org>
```

Git even has a -s command line option to append this automatically to your commit message:

```
git commit -s -m 'This is my commit message'
```

## Pre-commit

We use pre-commit to prevent committing code not compliant with our guidelines, the configuration can be found in `.pre-commit-config.yaml`

> **Note**
> Before executing pre-commit in this repository, some dependencies need to be installed and configured once globally. More information can be found [here](https://github.com/trustedshops/aws-toolbox/blob/master/docs/docs/setting-up-pre-commit.md)

- Run this command once to active pre-commit in the repository

    ```bash
    pre-commit install
    ```

- Run all pre-commits hooks against all files

    ```bash
    pre-commit run --all-files
    ```

- Run all pre-commits hooks against a single file, e.g. variables.tf

    ```bash
    pre-commit run --files variables.tf
    ```
