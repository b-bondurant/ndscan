import h5py
import json
from typing import Any, Dict
from PyQt5 import QtCore
from .model import *


def emit_later(signal, *args):
    QtCore.QTimer.singleShot(0, lambda: signal.emit(*args))


class HDF5Root(Root):
    """Scan root fed from an HDF5 results file."""

    def __init__(self, datasets: h5py.Group, context: Context):
        super().__init__()

        axes = json.loads(datasets["ndscan.axes"][()])
        dim = len(axes)
        if dim == 0:
            self._model = HDF5SingleShotModel(datasets, context)
        else:
            self._model = HDF5ScanModel(axes, datasets, context)
        emit_later(self.model_changed, self._model)

    def get_model(self) -> Model:
        return self._model


class HDF5SingleShotModel(SinglePointModel):
    def __init__(self, datasets: h5py.Group, context: Context):
        super().__init__(context)

        self._channel_schemata = json.loads(datasets["ndscan.channels"][()])
        emit_later(self.channel_schemata_changed, self._channel_schemata)

        self._point = {}
        for key in self._channel_schemata:
            self._point[key] = datasets["ndscan.point." + key][()]
        emit_later(self.point_changed, self._point)

    def get_channel_schemata(self) -> Dict[str, Any]:
        return self._channel_schemata

    def get_point(self) -> Dict[str, Any]:
        return self._point


class HDF5ScanModel(ScanModel):
    def __init__(self, axes: List[Dict[str, Any]], datasets: h5py.Group,
                 context: Context):
        super().__init__(axes, context)

        self._channel_schemata = json.loads(datasets["ndscan.channels"][()])
        emit_later(self.channel_schemata_changed, self._channel_schemata)

        self._point_data = {}
        for name in (["axis_{}".format(i) for i in range(len(self.axes))] +
                     ["channel_" + c for c in self._channel_schemata.keys()]):
            self._point_data[name] = datasets["ndscan.points." + name][:]
        emit_later(self.points_appended, self._point_data)

    def get_channel_schemata(self) -> Dict[str, Any]:
        return self._channel_schemata

    def get_point_data(self) -> Dict[str, Any]:
        return self._point_data
