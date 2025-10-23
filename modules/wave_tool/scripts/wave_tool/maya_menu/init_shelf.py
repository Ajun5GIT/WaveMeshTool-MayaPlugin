"""Mayaシェルフインストールモジュール.

WaveTool用のシェルフボタンを作成します。
"""
from typing import Optional, List
from maya import cmds


class ShelfConstants:
    """シェルフで使用する定数."""
    SHELF_NAME: str = "WaveTool"
    SHELF_LAYOUT: str = "ShelfLayout"
    BUTTON_IMAGE: str = "commandButton.png"
    BUTTON_LABEL: str = "WaveTool"
    BUTTON_COMMAND: str = "from wave_tool.ui.tool import show_wave_tool; show_wave_tool()"


def install_shelf() -> None:
    """WaveTool用シェルフを作成します."""
    if not cmds.layout(ShelfConstants.SHELF_LAYOUT, exists=True):
        cmds.evalDeferred("from wave_tool.maya_menu.init_shelf import install_shelf; install_shelf()")
        return

    if not cmds.shelfLayout(ShelfConstants.SHELF_NAME, exists=True):
        cmds.shelfLayout(ShelfConstants.SHELF_NAME, parent=ShelfConstants.SHELF_LAYOUT)

    existing_buttons: Optional[List[str]] = cmds.shelfLayout(
        ShelfConstants.SHELF_NAME,
        q=True,
        ca=True
    )
    if existing_buttons:
        for btn in existing_buttons:
            cmds.deleteUI(btn)

    cmds.shelfButton(
        parent=ShelfConstants.SHELF_NAME,
        command=ShelfConstants.BUTTON_COMMAND,
        image=ShelfConstants.BUTTON_IMAGE,
        label=ShelfConstants.BUTTON_LABEL
    )