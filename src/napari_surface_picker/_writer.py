from typing import TYPE_CHECKING, Any, List, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import starfile
from magicgui.widgets import request_values
from scipy.spatial.transform import Rotation as R

from .utils import vec2euler

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def _layers_to_df(
    data: List["FullLayerData"], layer_column_name: str
) -> pd.DataFrame:
    """Turn a list of FullLayerData of vectors into a DataFrame with particle
    coordinates.
    """
    dfs = []
    for layer_data, meta, _layer_type in data:
        angles = np.rad2deg(vec2euler(layer_data[:, 1, :], True))
        df = pd.DataFrame(
            data={
                "rlnCoordinateX": layer_data[:, 0, 2],
                "rlnCoordinateY": layer_data[:, 0, 1],
                "rlnCoordinateZ": layer_data[:, 0, 0],
                "rlnAngleRot": angles[:, 0],
                "rlnAngleTilt": angles[:, 1],
                "rlnAnglePsi": angles[:, 2],
                layer_column_name: meta["name"].replace(" ", "_"),
            }
        )
        dfs.append(df)
    return pd.concat(dfs)


def _ensure_suffix(string: str, suffix: str) -> str:
    if string.endswith(suffix):
        return string
    return string + suffix


def write_star_warp(path: str, data: List["FullLayerData"]) -> List[str]:
    path = _ensure_suffix(path, ".star")
    particles = _layers_to_df(data, "rlnMicrographName")
    starfile.write(particles, path, overwrite=True)
    return [path]


def write_star_reliontomo(path: str, data: List["FullLayerData"]) -> List[str]:
    path = _ensure_suffix(path, ".star")
    particles = _layers_to_df(data, "rlnTomoName")
    # rlnAngleRot/Tilt/Psi -> rlnTomoSubtomogramRot/Tilt/Psi
    eulers = particles[["rlnAngleRot", "rlnAngleTilt", "rlnAnglePsi"]].to_numpy()
    rotated_basis = R.from_euler('y', angles=90, degrees=True).as_matrix()
    eulers = R.from_matrix(
        np.linalg.inv(rotated_basis) @ R.from_euler('ZYZ', eulers, degrees=True).as_matrix()
    ).as_euler(seq='ZYZ', degrees=True)
    rot_prior, tilt_prior, psi_prior = R.from_matrix(rotated_basis).as_euler(
        seq='ZYZ', degrees=True
    )
    particles[["rlnTomoSubtomogramRot", "rlnTomoSubtomogramTilt", "rlnTomoSubtomogramPsi"]] = eulers
    # lock rot/psi to 0 and tilt to 90
    particles["rlnAngleRot"] = rot_prior
    particles["rlnAngleTilt"] = tilt_prior
    particles["rlnAnglePsi"] = psi_prior
    particles["rlnAngleTiltPrior"] = tilt_prior
    particles["rlnAnglePsiPrior"] = psi_prior
    # Binning
    binning = request_values(binning=int, title="Enter tomogram binnings")[
        "binning"
    ]
    particles[[f"rlnCoordinate{xyz}" for xyz in "XYZ"]] *= binning
    starfile.write({"particles": particles}, path, overwrite=True)
    return [path]
