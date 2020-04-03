FROM python:3.6

LABEL maintainer="vinh-ngu@hotmail.com"

# Install deps
WORKDIR /app
ADD . .
RUN pip install -r requirements.txt

# Install kubectl
RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl"
RUN chmod +x kubectl
RUN ln -s /kubectl /usr/bin/kubectl

WORKDIR /app
CMD ["echo", "not implemented yet"]
