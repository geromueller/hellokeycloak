#-----------------------------------------------------------------------------
# BASE
#-----------------------------------------------------------------------------
FROM python:3.11-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

#-----------------------------------------------------------------------------
# BUILDER
#-----------------------------------------------------------------------------
FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry export --without-hashes -f requirements.txt | pip install -r /dev/stdin

COPY . .

RUN python -m venv /venv
RUN poetry build && /venv/bin/pip install dist/*.whl

#-----------------------------------------------------------------------------
# FINAL
#-----------------------------------------------------------------------------
FROM base as final

COPY --from=builder /venv /venv
CMD ["/venv/bin/serve"]