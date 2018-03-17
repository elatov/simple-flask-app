FROM python:3
COPY app app
WORKDIR app
RUN pip install -r requirements.txt
EXPOSE  8000
CMD ["python","app.py"]
