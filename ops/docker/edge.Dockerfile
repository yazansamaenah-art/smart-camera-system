FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y tesseract-ocr libglib2.0-0 libgl1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SERVER_URL=http://cloud:8000
ENV PIPELINE_BACKEND=opencv
CMD ["python","smartpole/edge/agent.py","--iterations","100","--fps","4","--server","http://cloud:8000","--backend","opencv"]
