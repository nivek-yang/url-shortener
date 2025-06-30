FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY ./backend /app/backend/
COPY ./frontend/templates /app/frontend/templates

WORKDIR /app/backend

RUN uv venv
RUN uv lock
RUN uv sync

ENV PATH="/app/backend/.venv/bin:$PATH"

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]