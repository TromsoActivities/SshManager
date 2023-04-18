ARG type

FROM python:3.10-alpine AS base
LABEL org.opencontainers.image.authors="ultraxime@yahoo.fr"

RUN apk update
# RUN apk update && apk add --update --no-cache py3-numpy
# ENV PYTHONPATH=/usr/lib/python3.10/site-packages

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -Ur requirements.txt

ENTRYPOINT ["python3", "main.py"]

EXPOSE 25564

HEALTHCHECK --interval=20s --timeout=2s --start-period=10s --retries=3 \
    CMD python3 main.py healthcheck

COPY . .

FROM base AS manager

CMD ["start", "manager"]

FROM base AS worker

CMD ["start", "worker"]

FROM ${type}
