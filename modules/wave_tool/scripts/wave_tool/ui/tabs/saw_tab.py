"""のこぎり波タブウィジェットモジュール."""
from typing import Optional, Dict, Any
from PySide6 import QtWidgets, QtCore
from wave_tool.ui.utils import create_right_aligned_widget, ParamKey, SpinBoxDefaults


class SawParamKey:
    """のこぎり波のパラメータキー定数."""
    LEFT_SLOPE: str = "left_slope"
    RIGHT_SLOPE: str = "right_slope"


class SawSpinBoxDefaults:
    """のこぎり波のスピンボックスデフォルト設定."""
    SLOPE_MIN: float = -100.0
    SLOPE_MAX: float = 100.0
    SLOPE_DEFAULT: float = 1.0
    SLOPE_DECIMALS: int = 3
    SLOPE_STEP: float = 0.1


class SawTab(QtWidgets.QWidget):
    """のこぎり波タブウィジェットクラス."""

    changed: QtCore.Signal = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, field_width: int = 120) -> None:
        """SawTabウィジェットのコンストラクタ.

        Args:
            parent: 親ウィジェット
            field_width: フィールドの幅
        """
        super().__init__(parent)
        self._field_width: int = field_width

        self.left_slope: QtWidgets.QDoubleSpinBox
        self.right_slope: QtWidgets.QDoubleSpinBox
        self.height: QtWidgets.QDoubleSpinBox

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
        self.left_slope = QtWidgets.QDoubleSpinBox()
        self.left_slope.setRange(SawSpinBoxDefaults.SLOPE_MIN, SawSpinBoxDefaults.SLOPE_MAX)
        self.left_slope.setDecimals(SawSpinBoxDefaults.SLOPE_DECIMALS)
        self.left_slope.setSingleStep(SawSpinBoxDefaults.SLOPE_STEP)
        self.left_slope.setValue(SawSpinBoxDefaults.SLOPE_DEFAULT)

        self.right_slope = QtWidgets.QDoubleSpinBox()
        self.right_slope.setRange(SawSpinBoxDefaults.SLOPE_MIN, SawSpinBoxDefaults.SLOPE_MAX)
        self.right_slope.setDecimals(SawSpinBoxDefaults.SLOPE_DECIMALS)
        self.right_slope.setSingleStep(SawSpinBoxDefaults.SLOPE_STEP)
        self.right_slope.setValue(SawSpinBoxDefaults.SLOPE_DEFAULT)

        self.height = QtWidgets.QDoubleSpinBox()
        self.height.setRange(SpinBoxDefaults.HEIGHT_MIN, SpinBoxDefaults.HEIGHT_MAX)
        self.height.setDecimals(SawSpinBoxDefaults.SLOPE_DECIMALS)
        self.height.setSingleStep(SawSpinBoxDefaults.SLOPE_STEP)
        self.height.setValue(SpinBoxDefaults.HEIGHT_DEFAULT)

    def _add_form_rows(self, form_layout: QtWidgets.QFormLayout) -> None:
        """フォームに行を追加します.

        Args:
            form_layout: フォームレイアウト
        """
        form_layout.addRow("左斜辺", create_right_aligned_widget(self.left_slope, self._field_width))
        form_layout.addRow("右斜辺", create_right_aligned_widget(self.right_slope, self._field_width))
        form_layout.addRow("高さ", create_right_aligned_widget(self.height, self._field_width))

    def _connect_signals(self) -> None:
        """シグナルを接続します."""
        for w in (self.left_slope, self.right_slope, self.height):
            w.valueChanged.connect(self.changed)

    def params(self) -> Dict[str, Any]:
        """現在のパラメータを取得します.

        Returns:
            パラメータ辞書
        """
        return {
            SawParamKey.LEFT_SLOPE: self.left_slope.value(),
            SawParamKey.RIGHT_SLOPE: self.right_slope.value(),
            ParamKey.HEIGHT: self.height.value(),
        }

    def set_params(self, params: Dict[str, Any]) -> None:
        """パラメータを設定します.

        Args:
            params: パラメータ辞書
        """
        if SawParamKey.LEFT_SLOPE in params:
            self.left_slope.blockSignals(True)
            self.left_slope.setValue(float(params[SawParamKey.LEFT_SLOPE]))
            self.left_slope.blockSignals(False)
        if SawParamKey.RIGHT_SLOPE in params:
            self.right_slope.blockSignals(True)
            self.right_slope.setValue(float(params[SawParamKey.RIGHT_SLOPE]))
            self.right_slope.blockSignals(False)
        if ParamKey.HEIGHT in params:
            self.height.blockSignals(True)
            self.height.setValue(float(params[ParamKey.HEIGHT]))
            self.height.blockSignals(False)
        self.changed.emit()