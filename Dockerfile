FROM python:3.10.0-slim AS poetry_builder
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN apt update && apt install -y curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

FROM poetry_builder as builder
RUN mkdir /build
WORKDIR /build
COPY cozifytemp ./cozifytemp
COPY poetry.lock pyproject.toml ./
RUN poetry build -f wheel

FROM python:3.10.0-slim
WORKDIR /srv
COPY --from=builder /build/dist/*.whl ./
RUN pip install *.whl

CMD ["cozifytemp-sample-loop"]
