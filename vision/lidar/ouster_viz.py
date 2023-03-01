from ouster import client
import numpy as np
import cv2
from contextlib import *
import matplotlib.pyplot as plt

# from sklearn.cluster import DBSCAN
import numpy.typing as npt
import imutils


def main():
    hostname = "os-122229001687.local"
    lidar_port = 7502

    # create empty config
    config: client.SensorConfig = client.SensorConfig()

    # set the values that you need: see sensor documentation for param meanings
    config.operating_mode = client.OperatingMode.OPERATING_NORMAL
    config.lidar_mode = client.LidarMode.MODE_1024x20
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
    stream: client._client.LidarScan
    with closing(client.Scans.stream(hostname, lidar_port, complete=False)) as stream:
        show: bool = True
        while show:
            scan: client.core.Scans
            for scan in stream:
                HSCALE = 2  # image viewer horizontal scale
                VSCALE = 8  # image viewer vertical scale
                # uncomment if you'd like to see frame id printed
                # print("frame id: {} ".format(scan.frame_id))

                # print(chr(27) + "[2J") # clear terminal

                # Range visualization
                range_field = scan.field(client.ChanField.RANGE)
                range_img = client.destagger(stream.metadata, range_field)  # destagger the range field
                range_img = (range_img / np.max(range_img) * 255).astype(np.uint8)  # convert to 8-bit viewable image

                cv2.imshow(
                    f"Range Image, (Upscale: {HSCALE}x width, {VSCALE}x height)",
                    cv2.resize(  # resize image to fit screen
                        range_img,
                        (range_img.shape[1] * HSCALE, range_img.shape[0] * VSCALE),
                        interpolation=cv2.INTER_AREA,
                    ),
                )
                # print(f"RANGE_FIELD IMAGE: {range_field=}, {range_field.shape=}, {range_field.dtype=}")
                # print(f"RANGE_FIELD IMAGE RANGE:\t\t {range_field.min()=}\t\t|\t{range_field.max()=}")

                # KMeans clustering of range image
                kmeans_img = _run_kmeans(range_img)
                cv2.imshow(
                    f"KMeans of Range Image, (Upscale: {HSCALE}x width, {VSCALE}x height)",
                    cv2.resize(
                        kmeans_img,
                        (kmeans_img.shape[1] * HSCALE, kmeans_img.shape[0] * VSCALE),
                        interpolation=cv2.INTER_AREA,
                    ),
                )

                # Obstacle detection with range field image
                RANGE_THRESH: int = 600  # mm
                obs_image = draw_obstacles(range_field, RANGE_THRESH)  # range threshold in mm
                cv2.imshow(
                    f"Obstacles within {RANGE_THRESH}mm of LiDAR, upscaled to {HSCALE}x width, {VSCALE}x height",
                    cv2.resize(
                        obs_image,
                        (obs_image.shape[1] * HSCALE, obs_image.shape[0] * VSCALE),
                        interpolation=cv2.INTER_AREA,
                    ),
                )

                # Signal visualization
                # signal_field = scan.field(client.ChanField.SIGNAL)
                # signal = client.destagger(stream.metadata, signal_field)
                # signal = (signal / np.max(signal) * 255).astype(np.uint8)
                # cv2.imshow(
                #     f"Signal Image, (Upscale: {HSCALE}x width, {VSCALE}x height)",
                #     cv2.resize(
                #         signal, (signal.shape[1] * HSCALE, signal.shape[0] * VSCALE), interpolation=cv2.INTER_AREA
                #     ),
                # )
                # print(f"SIGNAL_FIELD IMAGE: {signal_field=}, {signal_field.shape=}, {signal_field.dtype=}")
                # print(f"SIGNAL_FIELD IMAGE RANGE:\t\t {signal_field.min()=}\t\t|\t{signal_field.max()=}")

                # Reflectivity visualization
                reflectivity_field = scan.field(client.ChanField.REFLECTIVITY)
                reflectivity = client.destagger(stream.metadata, reflectivity_field)
                reflectivity = (reflectivity / np.max(reflectivity) * 255).astype(np.uint8)
                cv2.imshow(
                    f"Reflectivity Image, (Upscale: {HSCALE}x width, {VSCALE}x height)",
                    cv2.resize(
                        reflectivity,
                        (reflectivity.shape[1] * HSCALE, reflectivity.shape[0] * VSCALE),
                        interpolation=cv2.INTER_AREA,
                    ),
                )
                # print(f"REFLECTIVITY_IMAGE: {reflectivity_field=}, {reflectivity_field.shape=}, {reflectivity_field.dtype=}")
                # print(f"REFLECTIVITY_IMAGE RANGE:\t\t {reflectivity_field.min()=}\t|\t{reflectivity_field.max()=}")

                # Near-IR visualization
                # nearir_field = scan.field(client.ChanField.NEAR_IR)
                # nearir = client.destagger(stream.metadata, nearir_field)
                # nearir = (nearir / np.max(nearir) * 255).astype(np.uint8)
                # cv2.imshow(
                #     f"Near-IR Image, (Upscale: {HSCALE}x width, {VSCALE}x height)",
                #     cv2.resize(
                #         nearir, (nearir.shape[1] * HSCALE, nearir.shape[0] * VSCALE), interpolation=cv2.INTER_AREA
                #     ),
                # )
                # print(f"NEARIR_IMAGE: {nearir_field=}, {nearir_field.shape=}, {nearir_field.dtype=}")
                # print(f"NEARIR_IMAGE RANGE:\t\t\t {nearir_field.min()=}\t\t|\t{nearir_field.max()=}")

                cv2.waitKey(1)


def _run_kmeans(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Run kmeans with K=2 for color classification.
    """
    ## Image preprocessing to make text bigger/clearer ##
    blur: npt.NDArray[np.uint8] = cv2.medianBlur(image, ksize=9)

    kernel: npt.NDArray[np.uint8] = np.ones((5, 5), np.uint8)
    erosion: npt.NDArray[np.uint8] = cv2.erode(blur, kernel=kernel, iterations=1)
    dilated: npt.NDArray[np.uint8] = cv2.dilate(erosion, kernel=kernel, iterations=1)

    ## Color and Location-based KMeans clustering ##

    # Convert to (R, G, B, X, Y)
    vectorized: npt.NDArray[np.uint8] = dilated.flatten(order="A")
    idxs: npt.NDArray[np.uint8] = np.array([idx for idx, _ in np.ndenumerate(dilated)])
    vectorized = np.append(vectorized, idxs)

    # Run Kmeans with K=2
    term_crit: tuple[int, int, float] = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        10,
        1.0,
    )
    k_val: int = 10

    labels: npt.NDArray[np.str_]
    centers: npt.NDArray[np.float32]
    _, labels, centers = cv2.kmeans(
        np.float32(vectorized),
        K=k_val,
        bestLabels=None,
        criteria=term_crit,
        attempts=10,
        flags=0,
    )
    center_int: npt.NDArray[np.uint8] = centers.astype(np.uint8)

    # Convert back to BGR
    clustered_img = center_int[labels.flatten()[: labels.size // 3]].reshape((dilated.shape[0], dilated.shape[1]))
    # FIXME: ^^^ remove the //3 and add a *3 after dilated.shape[1] to unleash the demons

    # cv2.imshow(f"KMeans ({k_val=})", cv2.resize(clustered_img, (clustered_img.shape[1] * HSCALE, clustered_img.shape[0] * VSCALE), interpolation = cv2.INTER_AREA))

    return clustered_img


def draw_obstacles(image, range_):
    obs_thresh_img = np.where(image < range_, 0, 255).astype(np.uint8)
    obs_thresh_img = cv2.medianBlur(obs_thresh_img, ksize=9)
    _, thresh = cv2.threshold(obs_thresh_img, 127, 255, 0)  # threshold image for contours
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    obs_thresh_img = np.dstack((obs_thresh_img, obs_thresh_img, obs_thresh_img))  # turn into 3-channel image

    im_contours = imutils.grab_contours(contours)

    marked_image = np.copy(obs_thresh_img)

    for contour in im_contours:
        # compute the center of the contour
        moments = cv2.moments(contour)

        if moments["m00"] == 0:
            continue

        cnt_x = int(moments["m10"] / moments["m00"])
        cnt_y = int(moments["m01"] / moments["m00"])
        # draw the contour and center of the shape on the image
        cv2.drawContours(marked_image, [contour], -1, (0, 255, 0), 1)
        cv2.circle(marked_image, (cnt_x, cnt_y), 3, (0, 0, 255), -1)

    return marked_image


if __name__ == "__main__":
    main()
