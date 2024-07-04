FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

# install build tools & python
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libjpeg-dev \
    libpng-dev \
    build-essential \
    cmake \
    libprotobuf-dev \
    ffmpeg \
    g++ \
    git \
    graphicsmagick \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libfreetype6-dev \
    libgraphicsmagick1-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libpng-dev \
    libsm6 \
    libswscale-dev \
    libxext6 \
    libzmq3-dev \
    libxrender-dev \
    openslide-tools \
    pkg-config \
    protobuf-compiler \
    python3 \
    python3-dev \
    python3-pip \
    python3-tk \
    python3-lxml \
    python3-setuptools \
    python3-wheel \
    rsync \
    software-properties-common \
    unzip \
    wget \
    x11-xserver-utils \
    vim \
    zip

# install cleanup
RUN apt-get -qq update && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
# RUN pip3 install --no-cache-dir \
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir \
    argparse \
    cython \
    requests \
    protobuf \
    openpyxl \
    scikit-learn \
    ipykernel \
    jupyter \
    matplotlib \
    numpy \
    pandas \
    seaborn \
    scipy \
    transformers \
    datasets \
    torch \
    llama-parse llama-agents llama-index-llms-ollama llama-index \
    dspy-ai
    # rawpy \
    # cmake \
    # GitPython \
    # setuptools \
    # sentencepiece \
    # pillow \
    # llama-index-llms-huggingface-api llama-index-llms-huggingface llama-index-embeddings-huggingface \
    # langchain langgraph langchain-core langchain-community \
    # crewai \
    # autogen

# ENV TORCH_CUDA_ARCH_LIST="6.1"


# Install miniconda
# ENV PATH="${PATH}:/root/miniconda3/bin"

# RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#     && mkdir /root/.conda \
#     && bash Miniconda3-latest-Linux-x86_64.sh -b \
#     && rm -f Miniconda3-latest-Linux-x86_64.sh \
#     && conda update conda \
#     && conda install astunparse numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing_extensions future six requests dataclasses && \
#     conda install -y intel::mkl-static intel::mkl-include && \
#     conda install -y -c pytorch magma-cuda121 

# RUN rm -rf /root/miniconda3 
# RUN PATH=$(echo "$PATH" | sed -e 's/:\/root\/miniconda3\/bin$//')
# #ENV _GLIBCXX_USE_CXX11_ABI=1
# ENV CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
# RUN git clone --recursive https://github.com/pytorch/pytorch && \
#     cd pytorch && \
#     make triton && \
#     git checkout v2.1.0 && \
#     # if you are updating an existing checkout
#     git submodule sync && \
#     git submodule update --init --recursive && \
#     python3 setup.py develop

#RUN TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0" TORCH_NVCC_FLAGS="-Xfatbin -compress-all" \
#    CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

# ENTRYPOINT ["/bin/bash"]
