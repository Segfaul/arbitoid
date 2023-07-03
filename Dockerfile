FROM python:3.9

WORKDIR /app

COPY Arbitoid Arbitoid
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "Arbitoid.api:app", "--reload", "--log-level", "error"]

CMD ["python", "-m", "Arbitoid.global_parser"]

CMD ["python", "-m", "Arbitoid.__init__"]
