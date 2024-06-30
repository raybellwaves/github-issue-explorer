# {{cookiecutter.github_repository}}-issue-explorer

## CLI commands

To update your repo with the latest template run:
```
cruft update
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

Just scrape open issues:
```
cd {{cookiecutter.github_repository}}-issue-explorer
python main.py --states open --content_types issues --verbose True
```

Scrape open and closed issues and open and closed prs
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
