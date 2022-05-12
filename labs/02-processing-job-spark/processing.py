import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
install("pyarrow")

import argparse
import csv
import os
import pandas as pd
import pyarrow
from pyspark.sql import SparkSession
import pyspark.sql.functions as fn
from pyspark.sql.functions import pandas_udf, PandasUDFType
from pyspark.sql.types import StructType, StructField, ArrayType, DoubleType, StringType, IntegerType
import random
import shutil
import sys
import time
import traceback

schema = "date TIMESTAMP, client STRING, value FLOAT"
# pandasUDFs require an output schema. This one matches the format required for DeepAR
dataset_schema = StructType(
    [StructField("target", ArrayType(DoubleType())),
     StructField("cat", ArrayType(IntegerType())),
     StructField("start", StringType())
    ])

def create_session():
    try:
        spark = SparkSession.builder \
                .appName("PySparkApp") \
                .getOrCreate()
        
        print("SPARK_DRIVER_MEMORY: {}".format(spark.sparkContext._conf.get('spark.driver.memory')))
        print("SPARK_EXECUTOR_MEMORY: {}".format(spark.sparkContext._conf.get('spark.executor.memory')))
        
        return spark
    except Exception as e:
        stacktrace = traceback.format_exc()
        print("{}".format(stacktrace))

        raise e

def extract_data(spark, args):
    try:
        return spark \
            .read \
            .schema(schema) \
            .options(sep =',', header=True, mode="FAILFAST", timestampFormat="yyyy-MM-dd HH:mm:ss") \
            .csv(args.s3_input_file)
    except Exception as e:
        stacktrace = traceback.format_exc()
        print("{}".format(stacktrace))

        raise e
    
def load_data(spark, args, df):
    try:
        df.coalesce(1).write.mode('append').json(args.s3_output_path)
    except Exception as e:
        stacktrace = traceback.format_exc()
        print("{}".format(stacktrace))

        raise e

def transform_data(spark, args):
    df = extract_data(spark, args)
    
    # resample from 15min intervals to one hour to speed up training
    df = df \
        .groupBy(fn.date_trunc("HOUR", fn.col("date")).alias("date"), fn.col("client")) \
        .agg(fn.mean("value").alias("value"))
    
    # create a dictionary to Integer encode each client
    client_list = df.select("client").distinct().collect()
    client_list = [rec["client"] for rec in client_list]
    client_encoder = dict(zip(client_list, range(len(client_list)))) 
    
    random_client_list = random.sample(client_list, 6)

    random_clients_pandas_df = df \
                                .where(fn.col("client").isin(random_client_list)) \
                                .groupBy("date") \
                                .pivot("client").max().toPandas()

    random_clients_pandas_df.set_index("date", inplace=True)
    
    weekday_counts = df \
                .withColumn("dayofweek", fn.dayofweek("date")) \
                .groupBy("client") \
                .pivot("dayofweek") \
                .count()
    
    weekday_counts.agg(*[fn.min(col) for col in weekday_counts.columns[1:]]).show() # show minimum counts of observations across all clients
    weekday_counts.agg(*[fn.max(col) for col in weekday_counts.columns[1:]]).show() # show maximum counts of observations across all clients
    
    train_start_date = df.select(fn.min("date").alias("date")).collect()[0]["date"]
    test_start_date = "2014-01-01"
    end_date = df.select(fn.max("date").alias("date")).collect()[0]["date"]
    
    # split the data into train and test set
    train_data = df.where(fn.col("date") < test_start_date)
    test_data = df.where(fn.col("date") >= test_start_date)
    
    @pandas_udf(dataset_schema, PandasUDFType.GROUPED_MAP)
    def prep_deep_ar(df):

        df = df.sort_values(by="date")
        client_name = df.loc[0, "client"]
        targets = df["value"].values.tolist()
        cat = [client_encoder[client_name]]
        start = str(df.loc[0,"date"])

        return pd.DataFrame([[targets, cat, start]], columns=["target", "cat", "start"])
    
    train_data = train_data.groupBy("client").apply(prep_deep_ar)
    
    load_data(spark, args, train_data)

def main():
    parser = argparse.ArgumentParser(description="app inputs and outputs")
    parser.add_argument("--s3_input_file", type=str, help="s3 input bucket")
    parser.add_argument("--s3_output_path", type=str, help="s3 input key prefix")
    
    args = parser.parse_args()
    
    spark = create_session()
    
    transform_data(spark, args)
    
if __name__ == "__main__":
    main()