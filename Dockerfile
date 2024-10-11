FROM nvidia/cuda:12.1.0-runtime-ubuntu20.04

# Set environment variables
WORKDIR /app

# Install required system packages and Python
RUN apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    git \
    python3.10 \
    python3-pip
# Custom Lean 4 installation script without Visual Studio Code
RUN curl -y https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Copy the requirements.txt file
RUN pip3 install packaging torch==2.2.1
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Build Mathlib4 during the image build
# WORKDIR /app/mathlib4
# RUN lake exe cache get && lake build

# Set default work directory back to project root
WORKDIR /app

# Expose port if needed (optional)
# EXPOSE 8080

CMD ["bash"]

