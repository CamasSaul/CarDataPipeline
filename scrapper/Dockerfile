FROM python:3.13.15-slim

WORKDIR /scrapper

COPY . .

RUN pip install -e .

RUN playwright install firefox

CMD ["python", "scrapping.py"]