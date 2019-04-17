# -*- coding: utf-8 -*-

from kafka import KafkaConsumer
from pyspark.sql import SparkSession


def consumeData(spark, topic):
    '''
    Consumer consumes tweets from producer
    '''
    # set-up a Kafka consumer
    consumer = KafkaConsumer(topic)
    for msg in consumer:
        temp = (msg.value).decode("utf-8").split("||")
        print(temp[0])
        print(temp[1])

if __name__ == "__main__":

    spark = SparkSession.builder \
        .master("local") \
        .appName("Crawler") \
        .getOrCreate()

    # Variables
    topic = "News"

    consumeData(spark, topic)
