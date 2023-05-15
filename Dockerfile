# syntax=docker/dockerfile:1.2


# base
FROM python:3.11.1-alpine3.17 AS base
RUN apk add --no-cache tesseract-ocr


# build
FROM base AS build
WORKDIR /build
COPY requirements.txt .
RUN pip3 wheel --wheel-dir=/wheels -r requirements.txt


# test
FROM base AS test
RUN apk add --no-cache ttf-liberation
WORKDIR /app
COPY --from=build /wheels /wheels
COPY . .
RUN pip3 install \
  --no-index \
  --no-cache-dir \
  --find-links=/wheels \
  -r requirements.txt
RUN ["python3", "-m", "unittest", "-v", "tests"]


# prod
FROM base AS prod
WORKDIR /app
COPY --from=build /wheels /wheels
COPY . .
RUN pip3 install \
  --no-index \
  --no-cache-dir \
  --find-links=/wheels \
  -r requirements.txt
EXPOSE 5000/tcp
ENV FLASK_APP=tesseract_api
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
