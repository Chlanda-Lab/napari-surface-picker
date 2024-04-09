import dynamotable.constants
import dynamotable.utils
import numpy as np
import starfile
import dynamotable
import pandas as pd
from typing import TYPE_CHECKING, Any, List, Sequence, Tuple, Union
from .utils import vec2euler

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_starfile(path: str, data: Any, meta: dict) -> List[str]:
    angles = np.rad2deg(vec2euler(data[:, 1, :], True))
    particles = pd.DataFrame(data={
        "rlnCoordinateX": data[:, 0, 2],
        "rlnCoordinateY": data[:, 0, 1],
        "rlnCoordinateZ": data[:, 0, 0],
        "rlnAngleRot": angles[:, 0],
        "rlnAngleTilt": angles[:, 1],
        "rlnAnglePsi": angles[:, 2],
        # "rlnTomoName": meta["name"].replace(" ", "_"),
    })
    starfile.write(particles, path, overwrite=True)
    return [path]