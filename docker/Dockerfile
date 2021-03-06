# FROM node:9.11 as static
# RUN mkdir -p /opt/static
# WORKDIR /opt/static
# COPY taskhub/src/static /opt/static
# RUN yarn

FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/srv/taskhub
WORKDIR /opt/srv/taskhub

RUN pip install poetry
RUN poetry config settings.virtualenvs.create false
COPY poetry.lock pyproject.toml README.md /opt/srv/taskhub/
RUN mkdir -p /opt/srv/taskhub/src/taskhub
RUN touch /opt/srv/taskhub/src/taskhub/__init__.py
RUN poetry install -n

COPY src /opt/srv/taskhub/src

# COPY --from=static /opt/static/node_modules /opt/srv/taskhub/src/taskhub/static/node_modules
RUN cd src && taskhub/manage.py collectstatic --no-input --clear

EXPOSE 8000
CMD ["gunicorn", "-c", "docker/services/gunicorn/conf.py", "--bind", ":8000", "--chdir", "src/taskhub", "core.wsgi:application"]
