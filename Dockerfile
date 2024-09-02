FROM python:3.10-slim

WORKDIR /root

# install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
      bzip2 \
      g++ \
      git \
      graphviz \
      libgl1-mesa-glx \
      libhdf5-dev \
      openmpi-bin \
      wget \
      libzbar0 \
      default-jre \
      python3-tk && \
    rm -rf /var/lib/apt/lists/*

# install unzip
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip

# install python libraries
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# copy necessary files
COPY api.py /root/
COPY utils /root/utils/
COPY data/ /root/data/

# unzip images
RUN unzip /root/data/images.zip -d /root/data/images/

# port
EXPOSE 8000

# run
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]