FROM python:3.12.7-slim

WORKDIR /auto_up_resume_bot

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
