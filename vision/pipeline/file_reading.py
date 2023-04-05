from vision.common.constants import CameraParameters

def read_image_parameters(json_path: str, img_path: str) -> CameraParameters:
    raise NotImplementedError


def get_image_paths() -> list[str]:
    raise NotImplementedError