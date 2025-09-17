FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y tesseract-ocr libglib2.0-0 libgl1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DATABASE_URL=sqlite:///./smartpole.db
ENV POLICY_FILE=cloud/policy/rules.yaml
EXPOSE 8000
CMD ["uvicorn","cloud.app:app","--host","0.0.0.0","--port","8000"]
