FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages and Python
RUN apt-get update && \
    apt-get install -y python3.10 python3-pip git curl psmisc sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.10 /usr/bin/python

ARG USERNAME
ARG USER_UID
ARG USER_GID

RUN groupadd -f -g $USER_GID $USERNAME \
&& useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
&& echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
&& chmod 0440 /etc/sudoers.d/$USERNAME

RUN mkdir -p /data /var/repl /app

RUN chown -R ${USERNAME}:${USERNAME} /data /var /app

# Custom Lean 4 installation script without Visual Studio Code
RUN curl -s -O https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh && \
    bash elan-init.sh -y && \
    rm -rf elan-init.sh

ENV PATH="/home/$USERNAME/.elan/bin:${PATH}"

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

WORKDIR /app

CMD ["/bin/bash"]

