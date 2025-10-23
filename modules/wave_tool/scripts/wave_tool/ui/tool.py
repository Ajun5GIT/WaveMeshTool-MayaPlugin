"""WaveToolメインUIモジュール."""
from typing import Optional, Type, Dict, Any
from PySide6 import QtWidgets, QtCore
from maya import cmds
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui

from wave_tool.ui.tabs.rect_tab import RectTab
from wave_tool.ui.tabs.saw_tab import SawTab
from wave_tool.ui.tabs.trapezoid_tab import TrapezoidTab
from wave_tool.ui.preview.preview_widget import WavePreview
from wave_tool.ui.utils import create_right_aligned_widget, FIELD_WIDTH
from wave_tool.framework.base_wave import BaseWave


def get_maya_main_window() -> QtWidgets.QWidget:
    """Mayaのメインウィンドウを取得します.

    Returns:
        MayaのメインウィンドウのQtウィジェット
    """
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


_wave_tool_instance: Optional['WaveTool'] = None


class WaveTool(QtWidgets.QDialog):
    """WaveToolメインダイアログクラス."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """WaveToolダイアログのコンストラクタ.

        Args:
            parent: 親ウィジェット
        """
        if parent is None:
            parent = get_maya_main_window()

        super().__init__(parent)
        self.setWindowTitle("WaveTool")
        self.setObjectName("WaveToolDialog")
        self.resize(620, 520)

        self._shape: Optional[BaseWave] = None
        self._is_updating_from_gui: bool = False
        self._mesh_created: bool = False

        self.preview: WavePreview
        self.units_spin: QtWidgets.QSpinBox
        self.depth_spin: QtWidgets.QDoubleSpinBox
        self.tabs: QtWidgets.QTabWidget
        self.rect_tab: RectTab
        self.saw_tab: SawTab
        self.trapezoid_tab: TrapezoidTab
        self.create_btn: QtWidgets.QPushButton
        self.name_label: QtWidgets.QLabel

        self._setup_ui()
        self._connect_signals()
        self._update_preview_only()

    def _setup_ui(self) -> None:
        """UIコンポーネントをセットアップします."""
        main_layout = QtWidgets.QVBoxLayout(self)

        self._setup_preview(main_layout)
        self._setup_common_params(main_layout)
        self._setup_tabs(main_layout)
        self._setup_buttons(main_layout)
        self._setup_status_label(main_layout)

    def _setup_preview(self, layout: QtWidgets.QVBoxLayout) -> None:
        """プレビューウィジェットをセットアップします.

        Args:
            layout: 追加先のレイアウト
        """
        self.preview = WavePreview()
        layout.addWidget(self.preview)

    def _setup_common_params(self, layout: QtWidgets.QVBoxLayout) -> None:
        """共通パラメータ（ユニット数、奥行き）をセットアップします.

        Args:
            layout: 追加先のレイアウト
        """
        top_wrap = QtWidgets.QHBoxLayout()
        top_wrap.addStretch()

        top_form_host = QtWidgets.QWidget()
        top_form = QtWidgets.QFormLayout(top_form_host)
        top_form.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        top_form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        top_form.setLabelAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self._create_units_spin()
        self._create_depth_spin()

        top_form.addRow("ユニット数", create_right_aligned_widget(self.units_spin))
        top_form.addRow("奥行き", create_right_aligned_widget(self.depth_spin))

        top_wrap.addWidget(top_form_host, 0, QtCore.Qt.AlignTop)
        top_wrap.addStretch()
        layout.addLayout(top_wrap)

    def _create_units_spin(self) -> None:
        """ユニット数スピンボックスを作成します."""
        self.units_spin = QtWidgets.QSpinBox()
        self.units_spin.setRange(1, 100)
        self.units_spin.setValue(3)
        self.units_spin.setFixedWidth(FIELD_WIDTH)

    def _create_depth_spin(self) -> None:
        """奥行きスピンボックスを作成します."""
        self.depth_spin = QtWidgets.QDoubleSpinBox()
        self.depth_spin.setRange(0.1, 100.0)
        self.depth_spin.setDecimals(2)
        self.depth_spin.setValue(1.0)
        self.depth_spin.setFixedWidth(FIELD_WIDTH)

    def _setup_tabs(self, layout: QtWidgets.QVBoxLayout) -> None:
        """波形タイプタブをセットアップします.

        Args:
            layout: 追加先のレイアウト
        """
        self.tabs = QtWidgets.QTabWidget()
        self.rect_tab = RectTab(field_width=FIELD_WIDTH)
        self.saw_tab = SawTab(field_width=FIELD_WIDTH)
        self.trapezoid_tab = TrapezoidTab(field_width=FIELD_WIDTH)

        self.tabs.addTab(self.rect_tab, "矩形")
        self.tabs.addTab(self.saw_tab, "のこぎり")
        self.tabs.addTab(self.trapezoid_tab, "台形波")
        layout.addWidget(self.tabs)

    def _setup_buttons(self, layout: QtWidgets.QVBoxLayout) -> None:
        """ボタン行をセットアップします.

        Args:
            layout: 追加先のレイアウト
        """
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        self.create_btn = QtWidgets.QPushButton("作成")
        btn_row.addWidget(self.create_btn)
        layout.addLayout(btn_row)

    def _setup_status_label(self, layout: QtWidgets.QVBoxLayout) -> None:
        """ステータスラベルをセットアップします.

        Args:
            layout: 追加先のレイアウト
        """
        self.name_label = QtWidgets.QLabel("対象オブジェクト: 未作成")
        layout.addWidget(self.name_label)

    def _connect_signals(self) -> None:
        """シグナルとスロットを接続します."""
        self.units_spin.valueChanged.connect(self._on_gui_changed)
        self.depth_spin.valueChanged.connect(self._on_gui_changed)
        self.rect_tab.changed.connect(self._on_gui_changed)
        self.saw_tab.changed.connect(self._on_gui_changed)
        self.trapezoid_tab.changed.connect(self._on_gui_changed)

        self.tabs.currentChanged.connect(self._update_preview_only)

        self.preview.requestParamUpdate.connect(self._apply_params_from_preview)
        self.create_btn.clicked.connect(self._on_create_clicked)

    def _get_current_params(self) -> Dict[str, Any]:
        """現在のパラメータ辞書を取得します.

        Returns:
            現在のパラメータ
        """
        params = {'units': self.units_spin.value(), 'depth': self.depth_spin.value()}
        idx = self.tabs.currentIndex()
        if idx == 0:
            params.update(self.rect_tab.params())
        elif idx == 1:
            params.update(self.saw_tab.params())
        else:
            params.update(self.trapezoid_tab.params())
        return params

    def _get_current_shape_class(self) -> Type[BaseWave]:
        """現在選択されている波形クラスを取得します.

        Returns:
            波形クラス(RectWave, SawWave, TrapezoidWave)
        """
        from wave_tool.framework.rect_wave import RectWave
        from wave_tool.framework.saw_wave import SawWave
        from wave_tool.framework.trapezoid_wave import TrapezoidWave
        return [RectWave, SawWave, TrapezoidWave][self.tabs.currentIndex()]

    def _on_gui_changed(self) -> None:
        """GUIの値が変更された時の処理."""
        if self._mesh_created:
            self._update_preview_and_mesh()
        else:
            self._update_preview_only()

    def _update_preview_only(self) -> None:
        """プレビューのみを更新します."""
        self._is_updating_from_gui = True
        params = self._get_current_params()
        ShapeClass = self._get_current_shape_class()
        if self._shape is None or not isinstance(self._shape, ShapeClass):
            self._shape = ShapeClass()
        self.preview.set_data(self._shape, params)
        if self._shape.mesh_name and cmds.objExists(self._shape.mesh_name):
            self.name_label.setText(f"対象オブジェクト: {self._shape.mesh_name}")
        else:
            self.name_label.setText("対象オブジェクト: 未作成 (作成ボタンを押してください)")
        self._is_updating_from_gui = False

    def _update_preview_and_mesh(self) -> None:
        """プレビューとメッシュを更新します."""
        self._is_updating_from_gui = True
        params = self._get_current_params()
        ShapeClass = self._get_current_shape_class()
        if self._shape is None or not isinstance(self._shape, ShapeClass):
            self._shape = ShapeClass()
        self.preview.set_data(self._shape, params)
        mesh = self._shape.create_polygon(params)
        self.name_label.setText(f"対象オブジェクト: {mesh}")
        self._is_updating_from_gui = False

    def _apply_params_from_preview(self, new_params: Dict[str, Any]) -> None:
        """プレビューからパラメータを適用します.

        Args:
            new_params: 新しいパラメータ
        """
        self.units_spin.setValue(int(round(new_params.get('units', self.units_spin.value()))))
        idx = self.tabs.currentIndex()
        if idx == 0:
            self.rect_tab.set_params(new_params)
        elif idx == 1:
            self.saw_tab.set_params(new_params)
        else:
            self.trapezoid_tab.set_params(new_params)

    def _on_create_clicked(self) -> None:
        """作成ボタンがクリックされた時の処理."""
        self._mesh_created = True
        self._update_preview_and_mesh()


def show_wave_tool() -> WaveTool:
    """WaveToolダイアログを表示します.

    Returns:
        作成されたWaveToolインスタンス
    """
    global _wave_tool_instance
    if _wave_tool_instance is not None:
        try:
            _wave_tool_instance.close()
            _wave_tool_instance.deleteLater()
        except:
            pass
        _wave_tool_instance = None
    _wave_tool_instance = WaveTool(parent=get_maya_main_window())
    _wave_tool_instance.show()
    return _wave_tool_instance