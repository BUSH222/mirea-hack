FROM python:3.11.9


COPY requirements.txt requirements.txt
RUN pip install PyPI
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc
    
RUN pip3 install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "cd /app && python dbloader.py && python main.py"]