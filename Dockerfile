FROM python:3.7.1-alpine3.8

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
COPY . ./
RUN pip install -e .

ENTRYPOINT ["hasurino"]
