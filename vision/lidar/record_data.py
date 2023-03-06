#!/usr/bin/python3
""" Record data from Ouster OS-1-32-U LiDAR sensor to pcap file."""

import os
import sys
import argparse
import time
from contextlib import closing
from datetime import datetime
from more_itertools import time_limited

from ouster import client, pcap

## Sensor identification and network configuration constants
HOSTNAME: str = "os-122229001687.local"  # sensor hostname, set as os-<serial number>.local
LIDAR_PORT: int = 7502  # UDP port to listen on for lidar data
IMU_PORT: int = 7503  # UDP port to listen on for imu data


def record_pcap(
    hostname: str,
    lidar_port: int = LIDAR_PORT,
    imu_port: int = IMU_PORT,
    fname_base: str | None = None,
    n_seconds: int = 10,
) -> None:
    """
    Record data from live sensor to pcap file.

    NOTE: Pcap files recorded this way only preserve the UDP data stream and
    not networking information, unlike capturing packets directly from a network
    interface with tools like tcpdump or wireshark.

    See the Ouster API docs of :py:func:`.pcap.record` for additional options for
    writing pcap files.

    Parameters
    ----------
    hostname : str
        hostname of the sensor
    lidar_port : int, optional, default=LIDAR_PORT
        UDP port to listen on for lidar data
    imu_port : int, optional, default=IMU_PORT
        UDP port to listen on for imu data
    fname_base : str, optional, default=None
        base filename to write to (without extension)
        If None, a filename will be auto-generated based on datetime and sensor metadata
    n_seconds : int, optional, default=10
        max seconds of time to record. (Ctrl-Z correctly closes streams)
    """
    out_fname_base: str | None = fname_base

    # connect to sensor and record lidar/imu packets
    with closing(client.Sensor(hostname, lidar_port, imu_port, buf_size=640)) as source:
        # make a descriptive filename for metadata/pcap files
        if not out_fname_base:
            print("\nNo output filename given, using default format.")
            time_part: str = datetime.now().strftime("%Y%m%d_%H%M%S")
            meta: client.SensorInfo = source.metadata
            out_fname_base = f"{meta.prod_line}_{meta.sn}_{meta.mode}_{time_part}"

        print(f"Saving sensor metadata to: {out_fname_base}.json")
        source.write_metadata(f"{out_fname_base}.json")

        print(f"Writing to: {out_fname_base}.pcap for {n_seconds} seconds (Ctrl-C to stop early)")
        source_it: time_limited[client.Packet] = time_limited(n_seconds, source)
        n_packets: int = pcap.record(source_it, f"{out_fname_base}.pcap")

        print(f"Captured {n_packets} packets")


def main() -> None:
    """Main driver function, parses arguments and calls record_pcap."""
    # parse input argument for pcap file as -i and output argument as -o
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        help="output file (without file extension)",
    )
    parser.add_argument(
        "-t",
        "--time",
        type=int,
        required=False,
        help="recording time (s) (default: 10)",
    )
    parser.add_argument(
        "-c",
        "--precount",
        type=int,
        required=False,
        help="pre-count time (s) (default: 0)",
    )

    args: argparse.Namespace = parser.parse_args()
    record_time: int = args.time if args.time else 10

    # check if output file exists
    if args.output and os.path.exists(f"{args.output}.pcap"):
        print("Output file already exists, overwrite? (y/n)")
        if input().lower() not in ("y", "yes"):
            print("Exiting...")
            sys.exit(1)

    output_dir: str | None = None
    if args.output:
        output_dir = args.output

    if args.precount:
        for i in range(args.precount):
            print(f"Recording data in {args.precount-i} seconds...")
            time.sleep(1)

    record_pcap(HOSTNAME, LIDAR_PORT, IMU_PORT, fname_base=output_dir, n_seconds=record_time)


if __name__ == "__main__":
    main()
