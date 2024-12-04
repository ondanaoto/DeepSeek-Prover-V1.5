FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages and Python
RUN apt-get update && \
    apt-get install -y python3.10 python3-pip git curl psmisc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Custom Lean 4 installation script without Visual Studio Code
RUN curl -s -O https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh && \
    bash elan-init.sh -y && \
    rm -rf elan-init.sh

# Set default work directory back to project root
WORKDIR /app

# Copy project codes
COPY ./requirements.txt /app/
COPY ./mathlib4 /var/mathlib4

RUN pip install packaging
RUN pip install torch==2.2.1
RUN pip install -r requirements.txt

WORKDIR /var/mathlib4
RUN ~/.elan/bin/lake exe cache get
RUN ~/.elan/bin/lake build
RUN ~/.elan/bin/lake exe graph

ENTRYPOINT [ "./mvgraph.sh" ]
