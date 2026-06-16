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

# get_version<3 must be pinned before scanpy: scanpy 1.6.0 depends on legacy_api_wrap,
# which calls get_version at import time; get_version>=3 changed _detect_vcs() signature.
# networkx==2.3: satisfies scanpy>=2.3; Graph.node removed in 2.4+ breaks STREAM.
RUN conda install -n stream_env pip -y && \
    /opt/miniconda/envs/stream_env/bin/python -m pip install "networkx==2.3" "get_version<3" scanpy==1.6.0

# Patch STREAM source: networkx 2.3 renamed spring_layout's random_state -> seed;
# also patch Graph.node -> Graph.nodes (removed in networkx 2.4+).
RUN STREAM=/opt/miniconda/envs/stream_env/lib/python3.7/site-packages/stream && \
    sed -i 's/nx\.spring_layout(flat_tree,random_state=/nx.spring_layout(flat_tree,seed=/g' $STREAM/extra.py $STREAM/core.py && \
    sed -i 's/flat_tree\.node\b/flat_tree.nodes/g; s/epg\.node\b/epg.nodes/g' $STREAM/extra.py $STREAM/core.py

# Patch STREAM for pandas compatibility: newer pandas rejects assigning an iterable
# to a single cell via .loc; use .at for single-cell writes and a loop for multi-column.
COPY patch_stream.py /tmp/patch_stream.py
RUN /opt/miniconda/envs/stream_env/bin/python /tmp/patch_stream.py

# Use non-display backend so matplotlib works headless without pre-importing it.
ENV MPLBACKEND=Agg

SHELL ["conda", "run", "-n", "stream_env", "/bin/bash", "-c"]
