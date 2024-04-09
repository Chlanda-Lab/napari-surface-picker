import numpy as np
import starfile
import pandas as pd
from typing import TYPE_CHECKING, Any, List, Sequence, Tuple, Union
from .utils import vec2euler

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_starfile(path: str, data: List["FullLayerData"]) -> List[str]:
    dfs = []
    for layer_data, meta, _layer_type in data:
        angles = np.rad2deg(vec2euler(layer_data[:, 1, :], True))
        df = pd.DataFrame(data={
            "rlnCoordinateX": layer_data[:, 0, 2],
            "rlnCoordinateY": layer_data[:, 0, 1],
            "rlnCoordinateZ": layer_data[:, 0, 0],
            "rlnAngleRot": angles[:, 0],
            "rlnAngleTilt": angles[:, 1],
            "rlnAnglePsi": angles[:, 2],
            "rlnMicrographName": meta["name"].replace(" ", "_"),
        })
        dfs.append(df)
    particles = pd.concat(dfs)
    starfile.write(particles, path, overwrite=True)
    return [path]