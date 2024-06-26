# Χρήση της επίσημης εικόνας Python ως βάση
FROM python:3.9

# Ορισμός του working directory
WORKDIR /app

# Αντιγραφή του requirements.txt και εγκατάσταση των εξαρτήσεων
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Αντιγραφή του υπόλοιπου κώδικα της εφαρμογής
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install requests

# Εκκίνηση της εφαρμογής
CMD ["python", "main.py"]
