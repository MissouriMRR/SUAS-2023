#!/usr/bin/python3
"""View data from a pcap file recorded with `record_data.py`."""

import os
import sys
import argparse

import cv2
import numpy as np
from nptyping import NDArray, Shape, UInt8, UInt32

from ouster import client, pcap
from ouster.sdk.examples.pcap import pcap_3d_one_scan


HSCALE_DEFAULT: int = 2  # horizontal scale of image viewer
VSCALE_DEFAULT: int = 8  # vertical scale of image viewer


def view_recording(
    pcap_file: str,
    meta_file: str,
    hscale: int = HSCALE_DEFAULT,
    vscale: int = VSCALE_DEFAULT,
    **viz_flags: bool,
) -> None:
    """
    View a pcap file recorded with `record_data.py`.

    Parameters
    ----------
    pcap_file : str
        Path to pcap file
    meta_file : str
        Path to metadata json file
    hscale : int, optional, default=HSCALE_DEFAULT
        Horizontal scale of image viewer, by default HSCALE_DEFAULT
    vscale : int, optional, default=VSCALE_DEFAULT
        Vertical scale of image viewer, by default VSCALE_DEFAULT
    **viz_flags : dict[str, bool]
        Flags for which visualizations to show.
        Options are:
            "range": Range visualization
            "reflectivity": Reflectivity visualization
            "signal": Signal visualization
            "nearir": Near infrared visualization
            "pointcloud": 3D point cloud visualization of first frame
    """
    viz_frame_delay: int = 50  # ms, modify this if the visualization video is too fast or too slow

    metadata: client.SensorInfo | None = None
    with open(meta_file, mode="r", encoding="UTF-8") as json_file:
        metadata = client.SensorInfo(json_file.read())

    source: pcap.Pcap = pcap.Pcap(pcap_path=pcap_file, info=metadata)

    if viz_flags.get("pointcloud"):
        pcap_3d_one_scan(source, metadata, num=0)  # view 3d point cloud of first frame of recording

    scan: client.core.Scans
    for scan in client.Scans(source):
        # print("frame id: {} ".format(scan.frame_id)) # uncomment to see frame id printed

        if viz_flags.get("range"):
            # Range visualization
            range_field: NDArray[Shape["32, 1024"], UInt32]
            range_field = scan.field(client.ChanField.RANGE)
            range_img: NDArray[Shape["32, 1024"], UInt8] = client.destagger(metadata, range_field)
            range_img = (range_img / np.max(range_img) * 255).astype(np.uint8)  # normalize image
            range_img = np.clip(range_img * 1.8, 0, 255).astype(np.uint8)  # increase brightness

            cv2.imshow(
                f"Range, (Upscale: {hscale}x width, {vscale}x height)",
                cv2.resize(  # resize image to fit screen
                    range_img,
                    (range_img.shape[1] * hscale, range_img.shape[0] * vscale),
                    interpolation=cv2.INTER_AREA,
                ),
            )

        if viz_flags.get("reflectivity"):
            # Reflectivity visualization
            refl_field: NDArray[Shape["32, 1024"], UInt32]
            refl_field = scan.field(client.ChanField.REFLECTIVITY)
            refl: NDArray[Shape["32, 1024"], UInt8] = client.destagger(metadata, refl_field)
            refl = (refl / np.max(refl) * 255).astype(np.uint8)  # normalize image
            refl = np.clip(refl * 2.2, 0, 255).astype(np.uint8)  # increase brightness
            cv2.imshow(
                f"Reflectivity, (Upscale: {hscale}x width, {vscale}x height)",
                cv2.resize(
                    refl,
                    (refl.shape[1] * hscale, refl.shape[0] * vscale),
                    interpolation=cv2.INTER_AREA,
                ),
            )

        if viz_flags.get("signal"):
            # Signal visualization
            signal_field: NDArray[Shape["32, 1024"], UInt32] = scan.field(client.ChanField.SIGNAL)
            signal: NDArray[Shape["32, 1024"], UInt8] = client.destagger(metadata, signal_field)
            signal = (signal / np.max(signal) * 255).astype(np.uint8)  # normalize image
            signal = np.clip(signal * 2.2, 0, 255).astype(np.uint8)  # increase brightness
            cv2.imshow(
                f"Signal, (Upscale: {hscale}x width, {vscale}x height)",
                cv2.resize(
                    signal,
                    (signal.shape[1] * hscale, signal.shape[0] * vscale),
                    interpolation=cv2.INTER_AREA,
                ),
            )

        if viz_flags.get("nearir"):
            # Near infrared visualization
            nearir_field: NDArray[Shape["32, 1024"], UInt32] = scan.field(client.ChanField.NEAR_IR)
            nearir: NDArray[Shape["32, 1024"], UInt8] = client.destagger(metadata, nearir_field)
            nearir = (nearir / np.max(nearir) * 255).astype(np.uint8)  # normalize image
            nearir = np.clip(nearir * 1.5, 0, 255).astype(np.uint8)  # increase brightness
            cv2.imshow(
                f"Near-IR, (Upscale: {hscale}x width, {vscale}x height)",
                cv2.resize(
                    nearir,
                    (nearir.shape[1] * hscale, nearir.shape[0] * vscale),
                    interpolation=cv2.INTER_AREA,
                ),
            )

        cv2.waitKey(viz_frame_delay)  # ms of additional delay between frames


def main() -> None:
    """
    Main driver function for pcap visualization.
    Parses command line arguments and calls pcap visualization function.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=False,
        help="REQUIRED: input pcap filename (with .pcap extension)",
    )
    parser.add_argument(
        "-hs",
        "--hscale",
        type=int,
        required=False,
        default=HSCALE_DEFAULT,
        help=f"Image view horizontal scale (default={HSCALE_DEFAULT})",
    )
    parser.add_argument(
        "-vs",
        "--vscale",
        type=int,
        default=VSCALE_DEFAULT,
        required=False,
        help=f"Image view vertical scale (default={VSCALE_DEFAULT})",
    )
    parser.add_argument(
        "-r",
        "--range",
        action="store_true",
        required=False,
        help="enable range visualization (enabled by default)",
    )
    parser.add_argument(
        "-f",
        "--reflectivity",
        action="store_true",
        required=False,
        help="enable reflectivity visualization",
    )
    parser.add_argument(
        "-s",
        "--signal",
        action="store_true",
        required=False,
        help="enable signal visualization",
    )
    parser.add_argument(
        "-n",
        "--nearir",
        action="store_true",
        required=False,
        help="enable near infrared visualization",
    )
    parser.add_argument(
        "-p",
        "--pointcloud",
        action="store_true",
        required=False,
        help="enable viewing of first-frame's point cloud in Open3D",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.input:
        # check if input file exists
        if not os.path.exists(args.input):
            print(
                f'Input path "{args.input}" does not exist!'
                + "Make sure to include the .pcap extension.'"
            )
            sys.exit(1)

        basename: str = os.path.splitext(args.input)[0]
        if any((args.range, args.reflectivity, args.signal, args.nearir, args.pointcloud)):
            view_recording(f"{basename}.pcap", f"{basename}.json", **vars(args))
        else:
            view_recording(f"{basename}.pcap", f"{basename}.json", range=True)
    else:
        print("No input file specified. Please specify an input file with the -i or --input flags.")
        print("Use -h or --help for more information.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
