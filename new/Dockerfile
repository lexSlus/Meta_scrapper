FROM python:3.11.2-alpine3.17

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./Pipfile.lock ./Pipfile ./

RUN apk add --update --no-cache postgresql-client build-base postgresql-dev \
                                musl-dev zlib zlib-dev linux-headers

RUN apk add --no-cache chromium
RUN apk add --no-cache chromium-chromedriver

RUN pip install --upgrade pip \
    # Install build tools for installing dependencies.
    pip install pipenv --trusted-host pypi.org --trusted-host files.pythonhosted.org && \
    pipenv requirements > requirements.txt && \
    # Install the PyPI dependencies using pip
    pip install --no-cache-dir -r requirements.txt

COPY ./scripts /scripts
RUN chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

COPY ./backend /app
WORKDIR /app

CMD ["/scripts/run.sh"]
