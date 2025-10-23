"""Maya起動時の初期化スクリプト."""
from maya import cmds
import maya.OpenMaya as om
from wave_tool.maya_menu.init_shelf import install_shelf


def _init() -> None:
    """初期化処理を実行します."""
    install_shelf()
    om.MGlobal.displayInfo("WaveTool: シェルフ登録完了")


cmds.evalDeferred(_init)