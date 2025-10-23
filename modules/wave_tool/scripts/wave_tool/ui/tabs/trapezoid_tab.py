"""台形波タブウィジェットモジュール."""
from typing import Optional, Dict, Any
from PySide6 import QtWidgets, QtCore
from wave_tool.ui.utils import create_right_aligned_widget, ParamKey, SpinBoxDefaults


class TrapezoidParamKey:
    """台形波のパラメータキー定数."""
    DIVISIONS_PER_UNIT: str = "divisions_per_unit"
    FLAT_TOP_WIDTH: str = "flat_top_width"
    EDGE_CURVATURE: str = "edge_curvature"


class TrapezoidSpinBoxDefaults:
    """台形波のスピンボックスデフォルト設定."""
    TRAPEZOID_WIDTH_DEFAULT: float = 3.0

    DIVISIONS_MIN: int = 2
    DIVISIONS_MAX: int = 200
    DIVISIONS_DEFAULT: int = 20

    FLAT_TOP_MIN: float = 0.0
    FLAT_TOP_MAX: float = 1.0
    FLAT_TOP_DEFAULT: float = 0.0
    FLAT_TOP_DECIMALS: int = 2
    FLAT_TOP_STEP: float = 0.05

    EDGE_CURVATURE_MIN: float = 0.5
    EDGE_CURVATURE_MAX: float = 10.0
    EDGE_CURVATURE_DEFAULT: float = 0.5
    EDGE_CURVATURE_DECIMALS: int = 1
    EDGE_CURVATURE_STEP: float = 0.5


class TrapezoidTab(QtWidgets.QWidget):
    """台形波タブウィジェットクラス."""

    changed: QtCore.Signal = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, field_width: int = 120) -> None:
        """TrapezoidTabウィジェットのコンストラクタ.

        Args:
            parent: 親ウィジェット
            field_width: フィールドの幅
        """
        super().__init__(parent)
        self._field_width: int = field_width

        self.width: QtWidgets.QDoubleSpinBox
        self.height: QtWidgets.QDoubleSpinBox
        self.div: QtWidgets.QSpinBox
        self.flat_top_width: QtWidgets.QDoubleSpinBox
        self.edge_curvature: QtWidgets.QDoubleSpinBox

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
        self.width = QtWidgets.QDoubleSpinBox()
        self.width.setRange(SpinBoxDefaults.WIDTH_MIN, SpinBoxDefaults.WIDTH_MAX)
        self.width.setValue(TrapezoidSpinBoxDefaults.TRAPEZOID_WIDTH_DEFAULT)

        self.height = QtWidgets.QDoubleSpinBox()
        self.height.setRange(SpinBoxDefaults.HEIGHT_MIN, SpinBoxDefaults.HEIGHT_MAX)
        self.height.setValue(SpinBoxDefaults.HEIGHT_DEFAULT)

        self.div = QtWidgets.QSpinBox()
        self.div.setRange(TrapezoidSpinBoxDefaults.DIVISIONS_MIN, TrapezoidSpinBoxDefaults.DIVISIONS_MAX)
        self.div.setValue(TrapezoidSpinBoxDefaults.DIVISIONS_DEFAULT)

        self.flat_top_width = QtWidgets.QDoubleSpinBox()
        self.flat_top_width.setRange(TrapezoidSpinBoxDefaults.FLAT_TOP_MIN, TrapezoidSpinBoxDefaults.FLAT_TOP_MAX)
        self.flat_top_width.setDecimals(TrapezoidSpinBoxDefaults.FLAT_TOP_DECIMALS)
        self.flat_top_width.setSingleStep(TrapezoidSpinBoxDefaults.FLAT_TOP_STEP)
        self.flat_top_width.setValue(TrapezoidSpinBoxDefaults.FLAT_TOP_DEFAULT)

        self.edge_curvature = QtWidgets.QDoubleSpinBox()
        self.edge_curvature.setRange(TrapezoidSpinBoxDefaults.EDGE_CURVATURE_MIN,
                                     TrapezoidSpinBoxDefaults.EDGE_CURVATURE_MAX)
        self.edge_curvature.setDecimals(TrapezoidSpinBoxDefaults.EDGE_CURVATURE_DECIMALS)
        self.edge_curvature.setSingleStep(TrapezoidSpinBoxDefaults.EDGE_CURVATURE_STEP)
        self.edge_curvature.setValue(TrapezoidSpinBoxDefaults.EDGE_CURVATURE_DEFAULT)

    def _add_form_rows(self, form_layout: QtWidgets.QFormLayout) -> None:
        """フォームに行を追加します.

        Args:
            form_layout: フォームレイアウト
        """
        form_layout.addRow("幅", create_right_aligned_widget(self.width, self._field_width))
        form_layout.addRow("高さ", create_right_aligned_widget(self.height, self._field_width))
        form_layout.addRow("1ユニット分割数", create_right_aligned_widget(self.div, self._field_width))
        form_layout.addRow("上部の幅", create_right_aligned_widget(self.flat_top_width, self._field_width))
        form_layout.addRow("曲率", create_right_aligned_widget(self.edge_curvature, self._field_width))

    def _connect_signals(self) -> None:
        """シグナルを接続します."""
        for w in (self.width, self.height, self.div, self.flat_top_width, self.edge_curvature):
            w.valueChanged.connect(self.changed)

    def params(self) -> Dict[str, Any]:
        """現在のパラメータを取得します.

        Returns:
            パラメータ辞書
        """
        return {
            ParamKey.WIDTH: self.width.value(),
            ParamKey.HEIGHT: self.height.value(),
            TrapezoidParamKey.DIVISIONS_PER_UNIT: self.div.value(),
            TrapezoidParamKey.FLAT_TOP_WIDTH: self.flat_top_width.value(),
            TrapezoidParamKey.EDGE_CURVATURE: self.edge_curvature.value(),
        }

    def set_params(self, params: Dict[str, Any]) -> None:
        """パラメータを設定します.

        Args:
            params: パラメータ辞書
        """
        if ParamKey.WIDTH in params:
            self.width.blockSignals(True)
            self.width.setValue(params[ParamKey.WIDTH])
            self.width.blockSignals(False)
        if ParamKey.HEIGHT in params:
            self.height.blockSignals(True)
            self.height.setValue(params[ParamKey.HEIGHT])
            self.height.blockSignals(False)
        if TrapezoidParamKey.DIVISIONS_PER_UNIT in params:
            self.div.blockSignals(True)
            self.div.setValue(int(params[TrapezoidParamKey.DIVISIONS_PER_UNIT]))
            self.div.blockSignals(False)
        if TrapezoidParamKey.FLAT_TOP_WIDTH in params:
            self.flat_top_width.blockSignals(True)
            self.flat_top_width.setValue(params[TrapezoidParamKey.FLAT_TOP_WIDTH])
            self.flat_top_width.blockSignals(False)
        if TrapezoidParamKey.EDGE_CURVATURE in params:
            self.edge_curvature.blockSignals(True)
            self.edge_curvature.setValue(params[TrapezoidParamKey.EDGE_CURVATURE])
            self.edge_curvature.blockSignals(False)
        self.changed.emit()