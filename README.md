# SageMaker end to end lab using Spark

In this repository, we are stepping through all the possible interaction between Amazon SageMaker Studio and PySpark.

By using a demonstrative dataset, we will perform data preparation steps by using Amazon SageMaker Studio and 
Amazon SageMaker Processing jobs.

The dataset and the example provided are officially publicly maintained in the official AWS repository
[SageMaker Studio EMR](https://github.com/aws-samples/sagemaker-studio-emr).

The content of this repository is based on the offical blogpost 
[Create and manage Amazon EMR Clusters from SageMaker Studio to run interactive Spark and ML workloads – Part 1](https://aws.amazon.com/blogs/machine-learning/part-1-create-and-manage-amazon-emr-clusters-from-sagemaker-studio-to-run-interactive-spark-and-ml-workloads/)

## Prerequisites:

In order to interact from Amazon SageMaker Studio with EMR, it's necessary to follow the setup described in the previosly 
linked blogpost.

Alternatively, it's possible to setup the environment by applying the [CloudFormation](./cloudformation) templates:
1. [00-secure_studio_template.yml](./cloudformation/00-secure_studio_template.yaml): This template creates a secure studio environment,
with VPC, Nat Gateway, Public and Private Subnets, and a Security Group for Studio
2. [01-emr_template.yml](./cloudformation/01-emr_template.yaml): This template creates the EMR cluster and links it to the networking
configuration defined for SageMaker Studio

Alternatively, it's possible to skip the previous step by adding the following prerequisites:

* Amazon SageMaker Studio Domain created
* S3 Endpoint created
* IAM Role linked to studio with EMR permissions

It's possible to create an EMR cluster by using the [Cloudformation](cloudformation/01-emr_template.yaml) template provided.

## Content of the lab

1. [PySpark in local mode](labs/00-notebook-local-pyspark/00-notebook-local-pyspark.ipynb)
2. [Data Processing using EMR from Studio](labs/01-notebook-sparkmagic-emr/01-spark-emr.ipynb)
3. [PySpark jobs using Amazon SageMaker Processing](labs/02-processing-job-spark/02-processing-job-spark.ipynb)