"""共通ユーティリティモジュール."""
from PySide6 import QtWidgets

FIELD_WIDTH: int = 80


class ParamKey:
    """パラメータ辞書のキー名を定義するクラス."""
    UNITS: str = "units"
    DEPTH: str = "depth"
    HEIGHT: str = "height"
    WIDTH: str = "width"


class SpinBoxDefaults:
    """スピンボックスのデフォルト値と範囲を定義するクラス."""

    UNITS_MIN: int = 1
    UNITS_MAX: int = 100
    UNITS_DEFAULT: int = 3

    DEPTH_MIN: float = 0.1
    DEPTH_MAX: float = 100.0
    DEPTH_DEFAULT: float = 1.0
    DEPTH_DECIMALS: int = 2

    WIDTH_MIN: float = 0.01
    WIDTH_MAX: float = 100.0
    WIDTH_DEFAULT: float = 1.0

    HEIGHT_MIN: float = 0.01
    HEIGHT_MAX: float = 100.0
    HEIGHT_DEFAULT: float = 1.0


def create_right_aligned_widget(widget: QtWidgets.QWidget, field_width: int = FIELD_WIDTH) -> QtWidgets.QWidget:
    """ウィジェットを右寄せするラッパーを作成します.

    Args:
        widget: 右寄せするウィジェット
        field_width: フィールドの幅（デフォルト: FIELD_WIDTH）

    Returns:
        右寄せレイアウトを持つラッパーウィジェット
    """
    widget.setFixedWidth(field_width)
    w = QtWidgets.QWidget()
    lay = QtWidgets.QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addStretch()
    lay.addWidget(widget)
    return w