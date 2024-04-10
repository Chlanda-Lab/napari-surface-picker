from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, Container, create_widget, PushButton
import numpy as np
from .cgal import Polyhedron

if TYPE_CHECKING:
    import napari

class SurfacePicker(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        # Surface layer
        self._in_surface_layer_combo = create_widget(
            label="Input surface",
            annotation="napari.layers.Surface"
        )
        # New surface layer
        self._out_surface_layer_combo = create_widget(
            label="Output surface",
            annotation="Optional[napari.layers.Surface]",
        )
        # Vectors layer
        self._out_vectors_layer_combo = create_widget(
            label="Vectors",
            annotation="Optional[napari.layers.Vectors]",
        )
        # Distance spinner
        self._distance_box = create_widget(
            label="Distance",
            annotation=float,
            widget_type="FloatSpinBox",
        )
        self._distance_box.value = 10
        # Invert checkbox
        self._invert_checkbox = CheckBox(value=False, label="Invert")
        # Shift Z spinner
        self._shift_z_box = create_widget(
            label="Shift Z",
            annotation=float,
            widget_type="FloatSpinBox",
        )
        self._shift_z_box.value = 0
        # Create output surface checkbox
        self._create_out_surface_checkbox = CheckBox(value=False, label="Create output surface (slow!)")
        # Sample button
        self.sample_button = PushButton(text="Sample")
        self.sample_button.changed.connect(self._sample)
        # Build widget
        self.extend(
            [
                self._in_surface_layer_combo,
                self._out_surface_layer_combo,
                self._out_vectors_layer_combo,
                self._distance_box,
                self._invert_checkbox,
                self._shift_z_box,
                self._create_out_surface_checkbox,
                self.sample_button,
            ]
        )

    def _sample(self, *args):
        if self._in_surface_layer_combo.value is self._out_surface_layer_combo:
            raise ValueError("Input and output surface cannot be the same!")
        surface_layer = self._in_surface_layer_combo.value
        if surface_layer is None:
            return
        if len(surface_layer.data) == 2:
            vertices, indices = surface_layer.data
        elif len(surface_layer.data) == 3:
            vertices, indices, _ = surface_layer.data
        else:
            return
        polyhedron = Polyhedron(vertices, indices)
        polyhedron.remove_isolated_vertices()
        polyhedron.isotropic_remeshing(self._distance_box.value)
        # Build output
        vertices = polyhedron.vertices_array()
        normals = polyhedron.compute_vertex_normals()
        assert len(vertices) == len(normals)
        # Surface layer
        if self._create_out_surface_checkbox.value:
            indices = polyhedron.indices_array()
            if self._out_surface_layer_combo.value is None:
                self._out_surface_layer_combo.value = self._viewer.add_surface((vertices, indices), name="Remeshed surface")
            else:
                self._out_surface_layer_combo.value.data = (vertices, indices)
        # Vectors layer
        # 1. Invert
        if self._invert_checkbox.value:
            normals *= -1
        # 2. Shift in Z
        vertices += normals * self._shift_z_box.value
        vectors_data = np.ndarray((len(vertices), 2, 3), dtype=float, order="C")
        vectors_data[:, 0, :] = vertices
        vectors_data[:, 1, :] = normals
        if self._out_vectors_layer_combo.value is None:
            self._out_vectors_layer_combo.value = self._viewer.add_vectors(
                vectors_data,
                name=f"{self._in_surface_layer_combo.value.name} particles",
                vector_style="arrow",
                blending="translucent"
            )
        else:
            self._out_vectors_layer_combo.value.data = vectors_data