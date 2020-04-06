FROM python:3.6

LABEL maintainer="vinh-ngu@hotmail.com"

# Install kubectl
RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl"
RUN chmod +x kubectl
RUN ln -s /kubectl /usr/bin/kubectl

# Install deps
WORKDIR /app
ADD . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
