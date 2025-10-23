"""矩形波クラスモジュール."""
from typing import Dict, Any, List, Tuple
from wave_tool.framework.base_wave import BaseWave, BaseWaveParamKey, BaseWaveConstants


class RectWaveParamKey:
    """矩形波のパラメータキー定数."""
    WIDTH_TOP: str = "width_top"
    WIDTH_BOTTOM: str = "width_bottom"
    CLOSE_END: str = "close_end"


class RectWaveConstants:
    """矩形波の定数."""
    DEFAULT_WIDTH_TOP: float = 1.0
    DEFAULT_WIDTH_BOTTOM: float = 1.0
    DEFAULT_CLOSE_END: bool = True


class RectWave(BaseWave):
    """矩形波クラス."""

    name: str = "rect"

    def unit_points(self, params: Dict[str, Any]) -> List[Tuple[float, float]]:
        """1ユニットの制御点リストを返します.

        Args:
            params: パラメータ辞書

        Returns:
            (X, Y)座標のリスト
        """
        width_top = float(params.get(RectWaveParamKey.WIDTH_TOP, RectWaveConstants.DEFAULT_WIDTH_TOP))
        width_bottom = float(params.get(RectWaveParamKey.WIDTH_BOTTOM, RectWaveConstants.DEFAULT_WIDTH_BOTTOM))
        h = float(params.get(BaseWaveParamKey.HEIGHT, BaseWaveConstants.DEFAULT_HEIGHT))
        return [
            (0.0, 0.0),
            (0.0, h),
            (width_top, h),
            (width_top, 0.0),
            (width_top + width_bottom, 0.0)
        ]

    def unit_length(self, params: Dict[str, Any]) -> float:
        """1ユニットの長さ(X方向)を返します.

        Args:
            params: パラメータ辞書

        Returns:
            ユニットの長さ
        """
        return (
            float(params.get(RectWaveParamKey.WIDTH_TOP, RectWaveConstants.DEFAULT_WIDTH_TOP)) +
            float(params.get(RectWaveParamKey.WIDTH_BOTTOM, RectWaveConstants.DEFAULT_WIDTH_BOTTOM))
        )

    def _needs_rebuild(self, params: Dict[str, Any]) -> bool:
        """ユニット数や深さが変わって頂点数が変化する時にTrueを返します.

        Args:
            params: パラメータ辞書

        Returns:
            再構築が必要な場合True
        """
        if not self._last_params:
            return True
        return (
            int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS)) !=
            int(self._last_params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))
            or int(params.get(BaseWaveParamKey.SY_DIVISIONS, BaseWaveConstants.DEFAULT_SY_DIVISIONS)) !=
            int(self._last_params.get(BaseWaveParamKey.SY_DIVISIONS, BaseWaveConstants.DEFAULT_SY_DIVISIONS))
            or float(params.get(BaseWaveParamKey.DEPTH, BaseWaveConstants.DEFAULT_DEPTH)) !=
            float(self._last_params.get(BaseWaveParamKey.DEPTH, BaseWaveConstants.DEFAULT_DEPTH))
            or bool(params.get(RectWaveParamKey.CLOSE_END, RectWaveConstants.DEFAULT_CLOSE_END)) !=
            bool(self._last_params.get(RectWaveParamKey.CLOSE_END, RectWaveConstants.DEFAULT_CLOSE_END))
        )

    def _calculate_x_divisions(self, params: Dict[str, Any], unit_pts: List[Tuple[float, float]]) -> int:
        """X方向の分割数を計算します（close_end対応）.

        Args:
            params: パラメータ辞書
            unit_pts: ユニットの点リスト

        Returns:
            X方向の分割数
        """
        units = int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))
        sx = units * (len(unit_pts) - 1)
        if params.get(RectWaveParamKey.CLOSE_END, RectWaveConstants.DEFAULT_CLOSE_END):
            sx -= 1
        return sx

    def apply_waveform(self, params: Dict[str, Any]) -> None:
        """polyPlaneの頂点へ波形を適用します（close_end対応）.

        Args:
            params: パラメータ辞書
        """
        unit_len = self.unit_length(params)
        units = int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))
        total_len = unit_len * units

        all_xy = self._build_xy_coordinates(params)

        unit_pts = self.unit_points(params)
        sx = units * (len(unit_pts) - 1)
        if params.get(RectWaveParamKey.CLOSE_END, RectWaveConstants.DEFAULT_CLOSE_END):
            sx -= 1
        num_x_verts = sx + 1

        self._apply_coordinates_to_mesh(all_xy, total_len, num_x_verts)