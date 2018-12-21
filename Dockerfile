FROM python:3.7.1-alpine3.8

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY . ./
RUN pipenv install --dev --system --deploy

ENTRYPOINT ["hasurino"]
