"""のこぎり波クラスモジュール."""
from typing import Dict, Any, List, Tuple
from wave_tool.framework.base_wave import BaseWave, BaseWaveParamKey, BaseWaveConstants


class SawWaveParamKey:
    """のこぎり波のパラメータキー定数."""
    LEFT_SLOPE: str = "left_slope"
    RIGHT_SLOPE: str = "right_slope"


class SawWaveConstants:
    """のこぎり波の定数."""
    DEFAULT_LEFT_SLOPE: float = 1.0
    DEFAULT_RIGHT_SLOPE: float = 1.0


class SawWave(BaseWave):
    """のこぎり波クラス."""

    name: str = "saw"

    def unit_points(self, params: Dict[str, Any]) -> List[Tuple[float, float]]:
        """1ユニットの制御点リストを返します.

        Args:
            params: パラメータ辞書

        Returns:
            (X, Y)座標のリスト
        """
        left = float(params.get(SawWaveParamKey.LEFT_SLOPE, SawWaveConstants.DEFAULT_LEFT_SLOPE))
        right = float(params.get(SawWaveParamKey.RIGHT_SLOPE, SawWaveConstants.DEFAULT_RIGHT_SLOPE))
        h = float(params.get(BaseWaveParamKey.HEIGHT, BaseWaveConstants.DEFAULT_HEIGHT))
        return [(0.0, 0.0), (left, h), (left + right, 0.0)]

    def unit_length(self, params: Dict[str, Any]) -> float:
        """1ユニットの長さ(X方向)を返します.

        Args:
            params: パラメータ辞書

        Returns:
            ユニットの長さ
        """
        return (
            float(params.get(SawWaveParamKey.LEFT_SLOPE, SawWaveConstants.DEFAULT_LEFT_SLOPE)) +
            float(params.get(SawWaveParamKey.RIGHT_SLOPE, SawWaveConstants.DEFAULT_RIGHT_SLOPE))
        )