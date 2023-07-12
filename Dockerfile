FROM python:3.11.4
WORKDIR /app
RUN pip install poetry
RUN pip install hypercorn
COPY . /app
RUN (cd /app && poetry install)
CMD ["poetry", "run", "hypercorn", "--bind", "0.0.0.0:5000", "app:app"]