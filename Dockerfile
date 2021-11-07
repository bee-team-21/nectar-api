FROM python:3.8-slim
WORKDIR /api/
ADD . /api/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--workers", "2", "--host", "0.0.0.0" ]