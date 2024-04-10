from typing import TYPE_CHECKING

from magicgui.widgets import Container, create_widget, PushButton
import numpy as np

if TYPE_CHECKING:
    import napari

class DipolePicker(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        # Surface layer
        self.in_shapes_layer_combo = create_widget(
            label="Input shapes",
            annotation="napari.layers.Shapes"
        )
        # Vectors layer
        self._out_vectors_layer_combo = create_widget(
            label="Vectors",
            annotation="Optional[napari.layers.Vectors]",
        )
        self.sample_button = PushButton(text="Sample")
        self.sample_button.changed.connect(self._sample)
        # Build widget
        self.extend(
            [
                self.in_shapes_layer_combo,
                self._out_vectors_layer_combo,
                self.sample_button,
            ]
        )

    def _sample(self, *args):
        shapes_layer = self.in_shapes_layer_combo.value
        if shapes_layer is None:
            return
        if not all(vec.shape == (2, 3) for vec in shapes_layer.data):
            raise ValueError("Invalid data shape")
        coords = [vec[0] for vec in shapes_layer.data]
        normals = np.array([vec[1] - vec[0] for vec in shapes_layer.data])
        normals /= np.linalg.norm(normals, axis=1)

        vectors_data = np.ndarray((len(coords), 2, 3), dtype=float)
        vectors_data[:, 0, :] = coords
        vectors_data[:, 1, :] = normals
        if self._out_vectors_layer_combo.value is None:
            self._out_vectors_layer_combo.value = self._viewer.add_vectors(
                vectors_data,
                name=f"{self.in_shapes_layer_combo.value.name} particles",
                vector_style="arrow",
                blending="translucent"
            )
        else:
            self._out_vectors_layer_combo.value.data = vectors_data