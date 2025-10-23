"""矩形波タブウィジェットモジュール."""
from typing import Optional, Dict, Any
from PySide6 import QtWidgets, QtCore
from wave_tool.ui.utils import create_right_aligned_widget, ParamKey, SpinBoxDefaults


class RectParamKey:
    """矩形波のパラメータキー定数."""
    WIDTH_TOP: str = "width_top"
    WIDTH_BOTTOM: str = "width_bottom"
    CLOSE_END: str = "close_end"


class RectTab(QtWidgets.QWidget):
    """矩形波タブウィジェットクラス."""

    changed: QtCore.Signal = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, field_width: int = 120) -> None:
        """RectTabウィジェットのコンストラクタ.

        Args:
            parent: 親ウィジェット
            field_width: フィールドの幅
        """
        super().__init__(parent)
        self._field_width: int = field_width

        self.width_top: QtWidgets.QDoubleSpinBox
        self.width_bottom: QtWidgets.QDoubleSpinBox
        self.height: QtWidgets.QDoubleSpinBox
        self.close_end: QtWidgets.QCheckBox

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """UIをセットアップします."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self._create_spinboxes()
        self._add_form_rows(form_layout)

        main_layout.addWidget(form_widget)

    def _create_spinboxes(self) -> None:
        """スピンボックスを作成します."""
        self.width_top = QtWidgets.QDoubleSpinBox()
        self.width_top.setRange(SpinBoxDefaults.WIDTH_MIN, SpinBoxDefaults.WIDTH_MAX)
        self.width_top.setValue(SpinBoxDefaults.WIDTH_DEFAULT)

        self.width_bottom = QtWidgets.QDoubleSpinBox()
        self.width_bottom.setRange(SpinBoxDefaults.WIDTH_MIN, SpinBoxDefaults.WIDTH_MAX)
        self.width_bottom.setValue(SpinBoxDefaults.WIDTH_DEFAULT)

        self.height = QtWidgets.QDoubleSpinBox()
        self.height.setRange(SpinBoxDefaults.HEIGHT_MIN, SpinBoxDefaults.HEIGHT_MAX)
        self.height.setValue(SpinBoxDefaults.HEIGHT_DEFAULT)

        self.close_end = QtWidgets.QCheckBox()
        self.close_end.setChecked(True)

    def _add_form_rows(self, form_layout: QtWidgets.QFormLayout) -> None:
        """フォームに行を追加します.

        Args:
            form_layout: フォームレイアウト
        """
        form_layout.addRow("上の幅", create_right_aligned_widget(self.width_top, self._field_width))
        form_layout.addRow("下の幅", create_right_aligned_widget(self.width_bottom, self._field_width))
        form_layout.addRow("高さ", create_right_aligned_widget(self.height, self._field_width))
        form_layout.addRow("末端を閉じる", create_right_aligned_widget(self.close_end, self._field_width))

    def _connect_signals(self) -> None:
        """シグナルを接続します."""
        for w in (self.width_top, self.width_bottom, self.height):
            w.valueChanged.connect(self.changed)
        self.close_end.stateChanged.connect(self.changed)

    def params(self) -> Dict[str, Any]:
        """現在のパラメータを取得します.

        Returns:
            パラメータ辞書
        """
        return {
            RectParamKey.WIDTH_TOP: self.width_top.value(),
            RectParamKey.WIDTH_BOTTOM: self.width_bottom.value(),
            ParamKey.HEIGHT: self.height.value(),
            RectParamKey.CLOSE_END: self.close_end.isChecked(),
        }

    def set_params(self, params: Dict[str, Any]) -> None:
        """パラメータを設定します.

        Args:
            params: パラメータ辞書
        """
        if RectParamKey.WIDTH_TOP in params:
            self.width_top.blockSignals(True)
            self.width_top.setValue(params[RectParamKey.WIDTH_TOP])
            self.width_top.blockSignals(False)
        if RectParamKey.WIDTH_BOTTOM in params:
            self.width_bottom.blockSignals(True)
            self.width_bottom.setValue(params[RectParamKey.WIDTH_BOTTOM])
            self.width_bottom.blockSignals(False)
        if ParamKey.HEIGHT in params:
            self.height.blockSignals(True)
            self.height.setValue(params[ParamKey.HEIGHT])
            self.height.blockSignals(False)
        if RectParamKey.CLOSE_END in params:
            self.close_end.blockSignals(True)
            self.close_end.setChecked(params[RectParamKey.CLOSE_END])
            self.close_end.blockSignals(False)
        self.changed.emit()