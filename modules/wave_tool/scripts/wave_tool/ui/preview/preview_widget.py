# -*- coding: utf-8 -*-
"""波形プレビューウィジェットモジュール.

波形データを視覚的にプレビューするためのウィジェットを提供します。
X/Yラベル、全長、比率表示機能を備えた左詰めレイアウトで表示します。
"""

from typing import Optional, Dict, Any, List, Tuple
from PySide6 import QtWidgets, QtCore, QtGui


class WavePreview(QtWidgets.QWidget):
    """波形プレビューウィジェットクラス.

    波形データを描画し、グリッド、座標軸、寸法情報を表示するウィジェットです。
    全体表示と比率表示をサポートし、自動的に画面に収まるよう調整します。
    """

    requestParamUpdate: QtCore.Signal = QtCore.Signal(dict)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """初期化メソッド.

        Args:
            parent: 親ウィジェット. デフォルトはNone.
        """
        super().__init__(parent)
        self._initialize_widget()
        self._initialize_wave_data()
        self._initialize_zoom_params()
        self._initialize_grid_params()

    def _initialize_widget(self) -> None:
        """ウィジェットの基本設定を初期化."""
        self.setMinimumHeight(250)

    def _initialize_wave_data(self) -> None:
        """波形データを初期化."""
        self.shape: Optional[Any] = None
        self.params: Dict[str, Any] = {}

    def _initialize_zoom_params(self) -> None:
        """ズームとオフセットパラメータを初期化."""
        self.base_zoom: float = 1.77
        self.zoom: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self._auto_fit_enabled: bool = True

    def _initialize_grid_params(self) -> None:
        """グリッドパラメータを初期化."""
        self._grid_unit: int = 1
        self._wave_width: float = 0.0
        self._wave_height: float = 0.0

    def set_data(self, shape: Any, params: Dict[str, Any]) -> None:
        """波形データを設定して再描画.

        Args:
            shape: 波形シェイプオブジェクト.
            params: 波形パラメータ辞書.
        """
        self.shape = shape
        self.params = params
        self._auto_fit_waveform()
        self.update()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """ウィンドウリサイズイベントハンドラ.

        Args:
            event: リサイズイベントオブジェクト.
        """
        super().resizeEvent(event)
        if self.shape and self.params:
            self._auto_fit_waveform()

    def _auto_fit_waveform(self) -> None:
        """波形全体が中央に収まるよう調整し、グリッド単位を決定."""
        if not self._validate_wave_data():
            return

        pts = self.shape.unit_points(self.params)
        if not pts or len(pts) < 2:
            return

        bounds = self._calculate_wave_bounds(pts)
        if not bounds:
            return

        width, height = bounds['width'], bounds['height']
        self._update_grid_unit(width)

        view_size = self._calculate_view_size()
        if not view_size:
            return

        self._calculate_zoom(width, height, view_size)
        self._calculate_offsets(bounds['min_x'], bounds['max_x'], bounds['min_y'], bounds['max_y'])

    def _validate_wave_data(self) -> bool:
        """波形データが有効かチェック.

        Returns:
            データが有効な場合True.
        """
        return self.shape is not None and self.params is not None

    def _calculate_wave_bounds(self, pts: List[Tuple[float, float]]) -> Optional[Dict[str, float]]:
        """波形の境界を計算.

        Args:
            pts: 波形の点リスト.

        Returns:
            境界情報辞書. Noneの場合は無効なデータ.
        """
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x
        height = max_y - min_y
        self._wave_width = width
        self._wave_height = height

        if width <= 0 or height <= 0:
            return None

        return {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'width': width,
            'height': height
        }

    def _update_grid_unit(self, width: float) -> None:
        """波形の幅に応じてグリッド単位を更新.

        Args:
            width: 波形の幅.
        """
        if width < 10:
            self._grid_unit = 1
        elif width < 100:
            self._grid_unit = 10
        else:
            self._grid_unit = 100

    def _calculate_view_size(self) -> Optional[Dict[str, float]]:
        """表示領域のサイズを計算.

        Returns:
            表示領域のサイズ辞書. Noneの場合は無効なサイズ.
        """
        margin = 40
        view_width = self.width() - margin * 2
        view_height = self.height() - margin * 2

        if view_width <= 0 or view_height <= 0:
            return None

        return {
            'width': view_width,
            'height': view_height
        }

    def _calculate_zoom(self, wave_width: float, wave_height: float, view_size: Dict[str, float]) -> None:
        """ズーム倍率を計算.

        Args:
            wave_width: 波形の幅.
            wave_height: 波形の高さ.
            view_size: 表示領域のサイズ辞書.
        """
        unit_size = 40 * self.base_zoom
        zoom_x = view_size['width'] / (wave_width * unit_size)
        zoom_y = view_size['height'] / (wave_height * unit_size)
        self.zoom = min(zoom_x, zoom_y)

    def _calculate_offsets(self, min_x: float, max_x: float, min_y: float, max_y: float) -> None:
        """オフセットを計算して波形を中央配置.

        Args:
            min_x: 最小X座標.
            max_x: 最大X座標.
            min_y: 最小Y座標.
            max_y: 最大Y座標.
        """
        eff_zoom = self.base_zoom * self.zoom
        scale = 40 * eff_zoom

        center_wave_x = (min_x + max_x) / 2
        center_wave_y = (min_y + max_y) / 2
        self.offset_x = -center_wave_x * scale
        self.offset_y = center_wave_y * scale

    def _draw_grid(self, painter: QtGui.QPainter, center_x: float, center_y: float, eff_zoom: float) -> None:
        """背景グリッドとラベル描画.

        Args:
            painter: QPainterオブジェクト.
            center_x: 画面中央のX座標.
            center_y: 画面中央のY座標.
            eff_zoom: 有効なズーム倍率.
        """
        grid_spacing = self._calculate_grid_spacing(eff_zoom)
        self._setup_grid_style(painter)

        self._draw_vertical_grid(painter, center_x, center_y, grid_spacing)
        self._draw_horizontal_grid(painter, center_x, center_y, grid_spacing)

    def _calculate_grid_spacing(self, eff_zoom: float) -> float:
        """グリッド間隔を計算.

        Args:
            eff_zoom: 有効なズーム倍率.

        Returns:
            グリッド間隔.
        """
        return self._grid_unit * 40 * eff_zoom

    def _setup_grid_style(self, painter: QtGui.QPainter) -> None:
        """グリッド描画スタイルを設定.

        Args:
            painter: QPainterオブジェクト.
        """
        painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 65), 1))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

    def _draw_vertical_grid(self, painter: QtGui.QPainter, center_x: float, center_y: float, grid_spacing: float) -> None:
        """垂直グリッド線とラベルを描画.

        Args:
            painter: QPainterオブジェクト.
            center_x: 画面中央のX座標.
            center_y: 画面中央のY座標.
            grid_spacing: グリッド間隔.
        """
        w = self.width()
        h = self.height()
        step_count = int(w / grid_spacing) + 2
        text_pen = QtGui.QPen(QtGui.QColor(170, 170, 170))
        grid_pen = QtGui.QPen(QtGui.QColor(60, 60, 65), 1)

        for i in range(-step_count, step_count + 1):
            line_x = center_x + i * grid_spacing
            if 0 <= line_x <= w:
                painter.setPen(grid_pen)
                painter.drawLine(int(line_x), 0, int(line_x), h)
                if i != 0:
                    painter.setPen(text_pen)
                    label = f"{i * self._grid_unit}"
                    painter.drawText(int(line_x) + 2, int(center_y) - 5, label)

    def _draw_horizontal_grid(self, painter: QtGui.QPainter, center_x: float, center_y: float, grid_spacing: float) -> None:
        """水平グリッド線とラベルを描画.

        Args:
            painter: QPainterオブジェクト.
            center_x: 画面中央のX座標.
            center_y: 画面中央のY座標.
            grid_spacing: グリッド間隔.
        """
        w = self.width()
        h = self.height()
        step_y = int(h / grid_spacing) + 2
        text_pen = QtGui.QPen(QtGui.QColor(170, 170, 170))
        grid_pen = QtGui.QPen(QtGui.QColor(60, 60, 65), 1)

        for j in range(-step_y, step_y + 1):
            line_y = center_y - j * grid_spacing
            if 0 <= line_y <= h:
                painter.setPen(grid_pen)
                painter.drawLine(0, int(line_y), w, int(line_y))
                if j != 0:
                    painter.setPen(text_pen)
                    label = f"{j * self._grid_unit}"
                    painter.drawText(int(center_x) + 5, int(line_y) - 2, label)

    def _draw_axes(self, painter: QtGui.QPainter, center_x: float, center_y: float) -> None:
        """座標軸描画.

        Args:
            painter: QPainterオブジェクト.
            center_x: 画面中央のX座標.
            center_y: 画面中央のY座標.
        """
        w = self.width()
        h = self.height()
        painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 110), 2))
        painter.drawLine(int(center_x), 0, int(center_x), h)
        painter.drawLine(0, int(center_y), w, int(center_y))

    def _draw_waveform(self, painter: QtGui.QPainter, center_x: float, center_y: float, eff_zoom: float) -> None:
        """波形描画.

        Args:
            painter: QPainterオブジェクト.
            center_x: 画面中央のX座標.
            center_y: 画面中央のY座標.
            eff_zoom: 有効なズーム倍率.
        """
        if not self.shape:
            return
        pts = self.shape.unit_points(self.params)
        if not pts:
            return

        screen_pts = self._convert_to_screen_coordinates(pts, center_x, center_y, eff_zoom)
        self._draw_waveform_lines(painter, screen_pts)
        self._draw_waveform_points(painter, screen_pts)

    def _convert_to_screen_coordinates(
        self,
        pts: List[Tuple[float, float]],
        center_x: float,
        center_y: float,
        eff_zoom: float
    ) -> List[QtCore.QPointF]:
        """波形座標を画面座標に変換.

        Args:
            pts: 波形の点リスト.
            center_x: 画面中央のX座標.
            center_y: 画面中央のY座標.
            eff_zoom: 有効なズーム倍率.

        Returns:
            画面座標のリスト.
        """
        scale = 40 * eff_zoom
        screen_pts = []
        for x, y in pts:
            screen_x = center_x + x * scale
            screen_y = center_y - y * scale
            screen_pts.append(QtCore.QPointF(screen_x, screen_y))
        return screen_pts

    def _draw_waveform_lines(self, painter: QtGui.QPainter, screen_pts: List[QtCore.QPointF]) -> None:
        """波形の線を描画.

        Args:
            painter: QPainterオブジェクト.
            screen_pts: 画面座標のリスト.
        """
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 220, 200), 3))
        painter.drawPolyline(QtGui.QPolygonF(screen_pts))

    def _draw_waveform_points(self, painter: QtGui.QPainter, screen_pts: List[QtCore.QPointF]) -> None:
        """波形の点を描画.

        Args:
            painter: QPainterオブジェクト.
            screen_pts: 画面座標のリスト.
        """
        painter.setBrush(QtGui.QBrush(QtGui.QColor(230, 80, 80)))
        painter.setPen(QtCore.Qt.NoPen)
        for pt in screen_pts:
            painter.drawEllipse(pt, 4, 4)

    def _draw_info_text(self, painter: QtGui.QPainter) -> None:
        """左上に波形の寸法情報と比率を描画.

        Args:
            painter: QPainterオブジェクト.
        """
        text = self._generate_info_text()
        self._setup_text_style(painter)
        painter.drawText(10, 18, text)

    def _generate_info_text(self) -> str:
        """情報テキストを生成.

        Returns:
            波形情報テキスト.
        """
        wv = self._wave_width
        hv = self._wave_height
        ratio = (wv / hv) if hv != 0 else 0
        return f"横幅:縦幅  {wv:.1f} : {hv:.1f}  （比率 1 : {ratio:.2f}）"

    def _setup_text_style(self, painter: QtGui.QPainter) -> None:
        """テキスト描画スタイルを設定.

        Args:
            painter: QPainterオブジェクト.
        """
        painter.setPen(QtGui.QPen(QtGui.QColor(220, 220, 220)))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """描画イベントハンドラ.

        Args:
            event: ペイントイベントオブジェクト.
        """
        painter = self._initialize_painter()
        center_x, center_y, eff_zoom = self._calculate_draw_parameters()

        self._draw_grid(painter, center_x, center_y, eff_zoom)
        self._draw_axes(painter, center_x, center_y)
        self._draw_waveform(painter, center_x, center_y, eff_zoom)
        self._draw_info_text(painter)

    def _initialize_painter(self) -> QtGui.QPainter:
        """ペインタを初期化.

        Returns:
            初期化されたペインタオブジェクト.
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(28, 28, 30))
        return painter

    def _calculate_draw_parameters(self) -> Tuple[float, float, float]:
        """描画パラメータを計算.

        Returns:
            (center_x, center_y, eff_zoom)のタプル.
        """
        w = self.width()
        h = self.height()
        center_x = w / 2.0 + self.offset_x
        center_y = h / 2.0 + self.offset_y
        eff_zoom = self.base_zoom * self.zoom
        return center_x, center_y, eff_zoom