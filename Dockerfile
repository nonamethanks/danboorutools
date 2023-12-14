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
COPY --chown=danboorutools:danboorutools celery_tasks.py /code/celery_tasks.py
RUN mkdir /code/screenshots /code/cookies
RUN mkdir /home/danboorutools/.ipython

RUN poetry install --no-interaction --no-ansi

ENV SHELL /bin/bash
ENV TERM xterm-256color

CMD poetry run watchmedo auto-restart -d /code/danboorutools -p="*" -R -- celery -- -A danboorutools.celery_tasks.tasks worker -B --loglevel=INFO -s /tmp/celerybeat-schedule
