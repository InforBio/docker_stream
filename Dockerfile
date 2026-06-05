FROM lijiaoning/inforbio:4.5.2

RUN apt-get update && apt-get install -y wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda && \
    rm Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/opt/miniconda/bin:$PATH"

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Add bioconda channel explicitly
RUN conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority strict

COPY env_STREAM.yml .
RUN conda env create -f env_STREAM.yml

# Fix h5py and unset R_HOME to avoid rpy2 segfault
RUN conda run -n stream_env conda install -c conda-forge h5py=2.10.0 --force-reinstall -y
RUN echo 'unset R_HOME' >> /root/.bashrc

SHELL ["conda", "run", "-n", "stream_env", "/bin/bash", "-c"]
