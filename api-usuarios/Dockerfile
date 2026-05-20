FROM python:3.13.3-slim

WORKDIR /home/app/

COPY requirements.txt .       
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .                       

EXPOSE 5002

CMD ["python", "app.py"]