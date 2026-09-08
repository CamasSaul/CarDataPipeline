FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

WORKDIR /scraper

COPY . .

RUN pip install -e .

RUN playwright install firefox

CMD ["python", "scraping.py"]