# github-issue-explorer

```
pip install cruft
```

```
cruft create git@github.com:raybellwaves/github-issue-explorer.git
```

## CLI commands

Install cruft and uv on your system however you prefer e.g. in you "base" env
```
pipx install cruft uv
```

Fill in the template like below
```
cruft create git@github.com:raybellwaves/github-issue-explorer.git
dask, dask, openai, ENTER
```

Create an environment for development
```
mamba create -n gie python=3.11 --y && \
  conda activate gie && \
  uv pip install -r requirements-dev.txt --find-links https://download.pytorch.org/whl/cpu
```

```
conda remove --name gie --all --y
```

```
cd {{cookiecutter.github_repository}}-issue-explorer
python main.py --states open --content_types issues --verbose True
```

## TODO

 - Could include timeline API which links issues/PRs
 - Haven't done anything with PR data

 ## See also

 - https://devlake.apache.org/
 - https://github.com/dlvhdr/gh-dash
