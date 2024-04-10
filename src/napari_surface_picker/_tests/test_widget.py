from typing import TYPE_CHECKING

from napari_surface_picker._sample_data import TUBE_VERTICES, TUBE_INDICES
from napari_surface_picker._surface_picker import SurfacePicker

if TYPE_CHECKING:
    import napari

def test_SurfacePicker(make_napari_viewer):
    viewer: "napari.Viewer" = make_napari_viewer()
    in_surface_layer = viewer.add_surface((TUBE_VERTICES, TUBE_INDICES))
    out_vectors_layer = viewer.add_vectors(ndim=3)

    widget = SurfacePicker(viewer)
    widget._in_surface_layer_combo.value = in_surface_layer
    widget._out_vectors_layer_combo.value = out_vectors_layer
    widget._distance_box.value = 10
    widget._sample()
    assert out_vectors_layer.data.shape == (1599, 2, 3)