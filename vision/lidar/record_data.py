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

HOSTNAME = "os-122229001687.local"
LIDAR_PORT = 7502
IMU_PORT = 7503


def record_pcap(
    hostname: str,
    lidar_port: int = 7502,
    imu_port: int = 7503,
    fname_base: str | None = None,
    n_seconds: int = 10,
) -> None:
    """Record data from live sensor to pcap file.

    Note that pcap files recorded this way only preserve the UDP data stream and
    not networking information, unlike capturing packets directly from a network
    interface with tools like tcpdump or wireshark.

    See the API docs of :py:func:`.pcap.record` for additional options for
    writing pcap files.

    Parameters
    ----------
    hostname : str
        hostname of the sensor
    lidar_port : int
        UDP port to listen on for lidar data
    imu_port : int
        UDP port to listen on for imu data
    fname_base : str, optional
        base filename to write to (without extension)
        If not specified, a filename will be generated
    n_seconds : int, optional, default=10
        max seconds of time to record. (Ctrl-Z correctly closes streams)
    """
    # connect to sensor and record lidar/imu packets
    with closing(client.Sensor(hostname, lidar_port, imu_port, buf_size=640)) as source:
        # make a descriptive filename for metadata/pcap files
        if not fname_base:
            print("\nNo output filename given, using default format.")
            time_part = datetime.now().strftime("%Y%m%d_%H%M%S")
            meta = source.metadata
            fname_base = f"{meta.prod_line}_{meta.sn}_{meta.mode}_{time_part}"

        print(f"Saving sensor metadata to: {fname_base}.json")
        source.write_metadata(f"{fname_base}.json")

        print(f"Writing to: {fname_base}.pcap for {n_seconds} seconds (Ctrl-C to stop early)")
        source_it = time_limited(n_seconds, source)
        n_packets = pcap.record(source_it, f"{fname_base}.pcap")

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
