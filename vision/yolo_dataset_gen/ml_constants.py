from typing import TypeAlias
from nptyping import NDArray, Shape, Float64


# Normalized Contour type
Norm_Ctr: TypeAlias = NDArray[Shape["*, 2"], Float64]