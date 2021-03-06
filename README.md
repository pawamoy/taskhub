# [ALPHA] TaskHub
Task management tool, supporting import/export from/to different services, with multiple interfaces.

## Requirements
`taskhub` requires Python 3.6. To install Python 3.6, I recommend [`pyenv`](https://github.com/pyenv/pyenv):
```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these two lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.7

# make it available globally
pyenv global system 3.6.7
```

## Installation
With `pip`:
```bash
python3.6 -m pip install taskhub
```

With [`pipx`](https://github.com/cs01/pipx):
```bash
# install pipx with the recommended method
curl https://raw.githubusercontent.com/cs01/pipx/master/get-pipx.py | python3

pipx install --python python3.6 taskhub
```
