import requests
import threading
import sys
import time
from datetime import datetime
from get_metric import cloud_watch_metrics


def call_end_point_http(url):
    headers = {'content-type': 'application/json'}
    res = requests.get(url, headers=headers)
    return res

def requests_get_n(url, n):
    """Makes a get request n times at the given url"""
    for i in range(n):
        call_end_point_http(url)


def get_1000_requests(url):
    requests_get_n(url, 1000)


def get_500_requests_1000_requests(url):
    requests_get_n(url, 500)
    time.sleep(60)
    requests_get_n(url, 1000)


def send_requests_1000(cluster_1_url, cluster_2_url):
    """Sets up 1000 requests threads"""
    start_time_1000 = datetime.utcnow()
    cluster_1_thread_1 = threading.Thread(
        target=get_1000_requests(cluster_1_url))
    cluster_2_thread_1 = threading.Thread(
        target=get_1000_requests(cluster_2_url))
    cluster_1_thread_1.start()
    cluster_2_thread_1.start()
    cluster_1_thread_1.join()
    cluster_2_thread_1.join()
    end_time_1000 = datetime.utcnow()
    time.sleep(10)
    print("Result for 1000 requests:")
    cloud_watch_metrics(start_time_1000, end_time_1000)


def send_requests_500_1_1000(cluster_1_url, cluster_2_url):
    """Sets up 500 requests threads"""
    start_time_500 = datetime.utcnow()
    cluster_1_thread_2 = threading.Thread(
        target=get_500_requests_1000_requests(cluster_1_url))
    cluster_2_thread_2 = threading.Thread(
        target=get_500_requests_1000_requests(cluster_2_url))
    cluster_1_thread_2.start()
    cluster_2_thread_2.start()
    cluster_1_thread_2.join()
    cluster_2_thread_2.join()
    end_time_500 = datetime.utcnow()
    print("Result for 500 requests - 60sec - 1000 requests:")
    cloud_watch_metrics(start_time_500, end_time_500)


if __name__ == "__main__":
    #Clusters URL(Load Balancer url/Target Groups)
    cluster_1_url = "http://T1-load-balancer-869731056.us-east-1.elb.amazonaws.com/cluster1"
    cluster_2_url = "http://T1-load-balancer-869731056.us-east-1.elb.amazonaws.com/cluster2"

    print("1000 GET requests sequentially:")
    send_requests_1000(cluster_1_url, cluster_2_url)

    print("E500 GET requests, then one minute sleep, followed by 1000 GET requests:")
    send_requests_500_1_1000(cluster_1_url, cluster_2_url)
