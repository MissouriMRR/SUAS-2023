from ouster import client
import numpy as np
import cv2
from contextlib import *
from sklearn.cluster import DBSCAN

hostname = "os-122229001687.local"
lidar_port = 7502

# create empty config
config = client.SensorConfig()

# set the values that you need: see sensor documentation for param meanings
config.operating_mode = client.OperatingMode.OPERATING_NORMAL
config.lidar_mode = client.LidarMode.MODE_1024x10
config.udp_port_lidar = 7502
config.udp_port_imu = 7503

# set the config on sensor, using appropriate flags
client.set_config(hostname, config, persist=True, udp_dest_auto=True)

# establish sensor connection
with closing(client.Scans.stream(hostname, lidar_port, complete=False)) as stream:
    show = True
    while show:
        for scan in stream:
            # uncomment if you'd like to see frame id printed
            # print("frame id: {} ".format(scan.frame_id))
            # reflectivity = client.destagger(stream.metadata, scan.field(client.ChanField.REFLECTIVITY))
            # reflectivity = (reflectivity / np.max(reflectivity) * 255).astype(np.uint8)

            ranges = scan.field(client.ChanField.RANGE)
            ranges_destaggered = client.destagger(stream.metadata, ranges)
            clustering = DBSCAN(eps=3, min_samples=2).fit(ranges_destaggered)
            cv2.imshow("name", clustering)
            key = cv2.waitKey(1)