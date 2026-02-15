FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

EXPOSE 8000

CMD [ "fastapi", "run", "./api.py" ]