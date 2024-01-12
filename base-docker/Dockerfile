FROM python:3.9

ENV CONDA_ENV /opt/conda-env

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl netbase wget \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /dev/null \
    && sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda \
    && rm -f Miniconda3-latest-Linux-x86_64.sh \
    && rm -rf /var/lib/apt/lists/*

COPY base-docker/vamo-conda-env.yml /tmp/environment.yml

RUN /opt/miniconda/bin/conda env create --file /tmp/environment.yml --prefix $CONDA_ENV \
    && $CONDA_ENV/bin/pip cache purge \
    && /opt/miniconda/bin/conda run -p $CONDA_ENV conda clean --yes --all

COPY python/chatbot_validator /chatbot_validator
COPY python/chatbot_cloud_util /chatbot_cloud_util

RUN /opt/miniconda/bin/conda run -p $CONDA_ENV pip install --no-cache-dir -e /chatbot_validator \
    && /opt/miniconda/bin/conda run -p $CONDA_ENV pip install --no-cache-dir -e /chatbot_cloud_util \
    && /opt/miniconda/bin/conda run -p $CONDA_ENV pip cache purge

ENTRYPOINT ["/opt/miniconda/bin/conda"]
CMD ["info"]
