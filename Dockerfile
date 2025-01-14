# Dockerfile
FROM python:3.12-slim

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

COPY requirements.txt ./

RUN apt-get update && apt-get install -y postgresql-client
RUN pip install -r requirements.txt

COPY api api
COPY migrations migrations
COPY alembic.ini alembic.ini
COPY main.py config.py boot.sh ./
# RUN chmod +x ./boot.sh

EXPOSE 5000
CMD ["./boot.sh"]