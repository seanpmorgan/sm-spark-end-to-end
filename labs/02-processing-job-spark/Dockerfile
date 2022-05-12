FROM 173754725891.dkr.ecr.us-east-1.amazonaws.com/sagemaker-spark-processing:2.4-cpu-py37-v1.1

# Do not change this argument
ARG APP_HOME=/opt/program

# Setup the environment path
ENV PATH="${APP_HOME}:${PATH}"

# Upgrade pip and setuptools
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools

# In this block we can copy our source code in the container
COPY src ${APP_HOME}

# In this block we can install our custom python modules
RUN pip3 install pandas scikit-learn s3fs

# Define the working directory
WORKDIR ${APP_HOME}

ENTRYPOINT ["smspark-submit", "processing.py"]
