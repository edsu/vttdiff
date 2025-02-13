# vttdiff

[![Tests](https://github.com/edsu/vttdiff/actions/workflows/test.yml/badge.svg)](https://github.com/edsu/vttdiff/actions/workflows/test.yml)

This is a small utility for "diffing" two (or more) WebVTT files and generating an HTML file like [this]. It was designed for comparing a "ground truth" WebVTT file with WebVTT files that might have been created with different software or services.
 
```
usage: vttdiff [-h] [--output OUTPUT] [--ignore-times] [--sentences] [--width WIDTH] vtt [vtt ...]

positional arguments:
  vtt              The path to two (or more) WebVTT files

options:
  -h, --help       show this help message and exit
  --output OUTPUT  Write output to this file path
  --ignore-times   Ignore cue times in the diff
  --sentences      Reorient lines as sentences
  --width WIDTH    The default width (in characters) of each transcript in the diff
```

So you could run it like:

```shell
% vttdiff --output diff.html first.vtt second.vtt
```

## Install

You should be able to pip install vttdiff:

```shell
$ pip3 install vttdiff
```

or just run it directly:

```shell
$ pipx run vttdiff
```

## Develop

*vttdiff* uses Python's [difflib] and is held together by duct tape and baling wire. If you have ideas for improving it please send a PR!

```
$ git clone git@github.com:edsu/vttdiff.git
$ uv run pytest
```

[this]: https://edsu.github.io/vttdiff/
[difflib]: https://docs.python.org/3/library/difflib.html
