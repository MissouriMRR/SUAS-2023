from ouster import client
import numpy as np
import cv2
from contextlib import *
import matplotlib.pyplot as plt
from PIL import Image

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

# with closing(client.Sensor(hostname, 7502, 7503)) as source:
#     # print some useful info from
#     print("Retrieved metadata:")
#     print(f"  serial no:        {source.metadata.sn}")
#     print(f"  firmware version: {source.metadata.fw_rev}")
#     print(f"  product line:     {source.metadata.prod_line}")
#     print(f"  lidar mode:       {source.metadata.mode}")
#     print(f"Writing to: {hostname}.json")

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
            print(ranges_destaggered)
            print(ranges_destaggered.shape)
            print(ranges_destaggered.dtype)
            cv2.imshow("name", ranges_destaggered)
            key = cv2.waitKey(1)

            # cv2.imshow("scaled reflectivity", reflectivity)
            # key = cv2.waitKey(1)
            # range_field = scan.field(client.ChanField.RANGE)
            # range_img = client.destagger(stream.metadata, range_field)
            # print(range_img)
            # print(range_img.shape)
            # plt.imshow(range_img, cmap='gray', resample=False)