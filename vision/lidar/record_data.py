from contextlib import closing
from ouster import client
from ouster.sdk import viz
from ouster.sdk.examples.client import record_pcap
from ouster.sdk.examples.pcap import pcap_to_csv
from ouster.sdk.examples.pcap import pcap_display_xyz_points
from ouster.sdk.examples.pcap import pcap_3d_one_scan
from ouster import pcap
import cv2
import numpy as np
import time

HOSTNAME = "os-122229001687.local"
LIDAR_PORT = 7502
IMU_PORT = 7503

FILENAME = "ouster_recording"

def record_pcap(hostname: str,
                lidar_port: int = 7502,
                imu_port: int = 7503,
                n_seconds: int = 10) -> None:
    """Record data from live sensor to pcap file.

    Note that pcap files recorded this way only preserve the UDP data stream and
    not networking information, unlike capturing packets directly from a network
    interface with tools like tcpdump or wireshark.

    See the API docs of :py:func:`.pcap.record` for additional options for
    writing pcap files.

    Args:
        hostname: hostname of the sensor
        lidar_port: UDP port to listen on for lidar data
        imu_port: UDP port to listen on for imu data
        n_seconds: max seconds of time to record. (Ctrl-Z correctly closes
                   streams)
    """
    import ouster.pcap as pcap
    from datetime import datetime

    # [doc-stag-pcap-record]
    from more_itertools import time_limited
    # connect to sensor and record lidar/imu packets
    with closing(client.Sensor(hostname, lidar_port, imu_port,
                               buf_size=640)) as source:

        # make a descriptive filename for metadata/pcap files
        time_part = datetime.now().strftime("%Y%m%d_%H%M%S")
        meta = source.metadata
        # fname_base = f"{meta.prod_line}_{meta.sn}_{meta.mode}_{time_part}"

        print(f"Saving sensor metadata to: {FILENAME}.json")
        source.write_metadata(f"{FILENAME}.json")

        print(f"Writing to: {FILENAME}.pcap (Ctrl-C to stop early)")
        source_it = time_limited(n_seconds, source)
        n_packets = pcap.record(source_it, f"{FILENAME}.pcap")

        print(f"Captured {n_packets} packets")

    # [doc-etag-pcap-record]

record_pcap(hostname=HOSTNAME, lidar_port=LIDAR_PORT, imu_port=IMU_PORT, n_seconds=10)

meta = None
with open(f"{FILENAME}.json", "r") as f:
    meta = client.SensorInfo(f.read())

source = pcap.Pcap(pcap_path=f"{FILENAME}.pcap", info=meta)

# pcap_3d_one_scan(source, meta, num=0)

# create an iterator of LidarScans from pcap and bound it if num is specified
scans = iter(client.Scans(source))

scan: client.core.Scans
for scan in scans:
    HSCALE = 2  # image viewer horizontal scale
    VSCALE = 8  # image viewer vertical scale
    # uncomment if you'd like to see frame id printed
    # print("frame id: {} ".format(scan.frame_id))

    # print(chr(27) + "[2J") # clear terminal

    # Range visualization
    range_field = scan.field(client.ChanField.RANGE)
    range_img = client.destagger(meta, range_field)  # destagger the range field
    range_img = (range_img / np.max(range_img) * 255).astype(np.uint8)  # convert to 8-bit viewable image

    cv2.imshow(
        f"Range Image, (Upscale: {HSCALE}x width, {VSCALE}x height)",
        cv2.resize(  # resize image to fit screen
            range_img,
            (range_img.shape[1] * HSCALE, range_img.shape[0] * VSCALE),
            interpolation=cv2.INTER_AREA,
        ),
    )
    