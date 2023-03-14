FROM archlinux:latest

ENV PYTHONUNBUFFERED 1

RUN pacman -Syyuu --noconfirm base-devel git unrar unzip atool vim tmux sqlite
RUN pacman -Syyuu --noconfirm chromium

RUN pacman -Syyuu --noconfirm pyenv

RUN useradd -ms /bin/bash danboorutools
USER danboorutools

ENV PYTHON_USER danboorutools
ENV PYENV_ROOT /home/${PYTHON_USER}/.pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}
ENV PYTHON_VERSION 3.11

RUN pyenv install ${PYTHON_VERSION}
RUN pyenv global ${PYTHON_VERSION}
RUN pyenv rehash

RUN which python
RUN python3 --version

RUN pip install -U pip poetry

WORKDIR /code
COPY --chown=danboorutools:danboorutools poetry.lock pyproject.toml /code/
COPY --chown=danboorutools:danboorutools danboorutools /code/danboorutools
RUN mkdir /code/screenshots /code/cookies
RUN mkdir /home/danboorutools/.ipython

RUN poetry install --no-interaction --no-ansi

# Fucking abandoned libraries, man
RUN rm -rf "$(poetry env info -p)/lib/python3.11/site-packages/tests"

ENV SHELL /bin/bash
ENV TERM xterm-256color
