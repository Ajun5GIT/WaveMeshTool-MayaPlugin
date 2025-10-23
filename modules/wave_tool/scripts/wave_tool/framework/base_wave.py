"""波形ポリゴンの基底クラスモジュール."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from maya import cmds


class BaseWaveParamKey:
    """基底波形クラスで使用するパラメータキー定数."""
    UNITS: str = "units"
    SY_DIVISIONS: str = "sy_divisions"
    DEPTH: str = "depth"
    HEIGHT: str = "height"
    WIDTH: str = "width"


class BaseWaveConstants:
    """基底波形クラスで使用する定数."""
    DEFAULT_UNITS: int = 1
    DEFAULT_SY_DIVISIONS: int = 1
    DEFAULT_DEPTH: float = 1.0
    DEFAULT_HEIGHT: float = 1.0
    DEFAULT_WIDTH: float = 1.0
    MERGE_VERTEX_DISTANCE: float = 0.001
    SCALE_FACTOR: float = 40.0


class BaseWave(ABC):
    """波形ポリゴンの基底クラス."""

    name: str = "wave"

    def __init__(self) -> None:
        """BaseWaveクラスのコンストラクタ."""
        self.mesh_name: Optional[str] = None
        self._last_params: Optional[Dict[str, Any]] = None

    @abstractmethod
    def unit_points(self, params: Dict[str, Any]) -> List[Tuple[float, float]]:
        """1ユニットの制御点リストを返します.

        Args:
            params: パラメータ辞書.

        Returns:
            (X, Y)座標のリスト.
        """
        raise NotImplementedError

    @abstractmethod
    def unit_length(self, params: Dict[str, Any]) -> float:
        """1ユニットの長さ(X方向)を返します.

        Args:
            params: パラメータ辞書.

        Returns:
            ユニットの長さ.
        """
        raise NotImplementedError

    def _needs_rebuild(self, params: Dict[str, Any]) -> bool:
        """ユニット数や深さが変わって頂点数が変化する時にTrueを返します.

        Args:
            params: パラメータ辞書.

        Returns:
            再構築が必要な場合True.
        """
        if not self._last_params:
            return True
        return (
            params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS) !=
            self._last_params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS) or
            params.get(BaseWaveParamKey.SY_DIVISIONS, BaseWaveConstants.DEFAULT_SY_DIVISIONS) !=
            self._last_params.get(BaseWaveParamKey.SY_DIVISIONS, BaseWaveConstants.DEFAULT_SY_DIVISIONS) or
            params.get(BaseWaveParamKey.DEPTH, BaseWaveConstants.DEFAULT_DEPTH) !=
            self._last_params.get(BaseWaveParamKey.DEPTH, BaseWaveConstants.DEFAULT_DEPTH)
        )

    def _build_xy_coordinates(self, params: Dict[str, Any]) -> List[Tuple[float, float]]:
        """全ユニットのXY座標リストを構築します.

        Args:
            params: パラメータ辞書.

        Returns:
            全頂点の(X, Y)座標リスト.
        """
        unit_pts: List[Tuple[float, float]] = self.unit_points(params)
        unit_len: float = self.unit_length(params)
        units: int = int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))

        all_xy: List[Tuple[float, float]] = []
        for u in range(units):
            offset: float = u * unit_len
            for i, (x, y) in enumerate(unit_pts):
                is_last: bool = (i == len(unit_pts) - 1)
                if u < units - 1 and is_last:
                    continue
                all_xy.append((offset + x, y))
        return all_xy

    def _save_transform(self) -> Optional[Dict[str, List[float]]]:
        """現在のメッシュのトランスフォームを保存します.

        Returns:
            トランスフォーム情報 (pos, rot, scale) または None.
        """
        if not self.mesh_name or not cmds.objExists(self.mesh_name):
            return None

        return {
            'pos': cmds.xform(self.mesh_name, q=True, ws=True, t=True),
            'rot': cmds.xform(self.mesh_name, q=True, ws=True, ro=True),
            'scale': cmds.xform(self.mesh_name, q=True, r=True, s=True)
        }

    def _restore_transform(self, transform: Optional[Dict[str, List[float]]]) -> None:
        """保存されたトランスフォームを復元します.

        Args:
            transform: トランスフォーム情報.
        """
        if not transform or not self.mesh_name:
            return

        if transform.get('pos'):
            cmds.xform(self.mesh_name, ws=True, t=transform['pos'])
        if transform.get('rot'):
            cmds.xform(self.mesh_name, ws=True, ro=transform['rot'])
        if transform.get('scale'):
            cmds.xform(self.mesh_name, r=True, s=transform['scale'])

    def _delete_existing_mesh(self) -> None:
        """既存のメッシュを削除します."""
        if self.mesh_name and cmds.objExists(self.mesh_name):
            cmds.delete(self.mesh_name)

    def _create_base_plane(self, params: Dict[str, Any]) -> str:
        """基本となるpolyPlaneを作成します.

        Args:
            params: パラメータ辞書.

        Returns:
            作成されたメッシュ名.
        """
        unit_len: float = self.unit_length(params)
        units: int = int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))
        total_len: float = unit_len * units
        depth: float = params.get(BaseWaveParamKey.DEPTH, BaseWaveConstants.DEFAULT_DEPTH)

        unit_pts: List[Tuple[float, float]] = self.unit_points(params)
        sx: int = self._calculate_x_divisions(params, unit_pts)
        sy: int = params.get(BaseWaveParamKey.SY_DIVISIONS, BaseWaveConstants.DEFAULT_SY_DIVISIONS)

        return cmds.polyPlane(
            w=total_len, h=depth, sx=sx, sy=sy, name=self.name
        )[0]

    def _calculate_x_divisions(
        self,
        params: Dict[str, Any],
        unit_pts: List[Tuple[float, float]]
    ) -> int:
        """X方向の分割数を計算します.

        Args:
            params: パラメータ辞書.
            unit_pts: ユニットの点リスト.

        Returns:
            X方向の分割数.
        """
        units: int = int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))
        return units * (len(unit_pts) - 1)

    def _apply_coordinates_to_mesh(
        self,
        all_xy: List[Tuple[float, float]],
        total_len: float,
        num_x_verts: int
    ) -> None:
        """メッシュの頂点に座標を適用します.

        Args:
            all_xy: 全頂点の(X, Y)座標リスト.
            total_len: 全体の長さ.
            num_x_verts: X方向の頂点数.
        """
        left: float = -total_len / 2.0

        try:
            vcount: int = cmds.polyEvaluate(self.mesh_name, vertex=True)
        except Exception:
            return

        for vid in range(vcount):
            pos: List[float] = cmds.pointPosition(f"{self.mesh_name}.vtx[{vid}]", local=True)
            x_idx: int = vid % num_x_verts
            if 0 <= x_idx < len(all_xy):
                x, y = all_xy[x_idx]
                cmds.move(
                    left + x, y, pos[2],
                    f"{self.mesh_name}.vtx[{vid}]",
                    absolute=True, objectSpace=True
                )

    def _flip_normals(self) -> None:
        """メッシュの法線を反転します."""
        if self.mesh_name:
            cmds.polyNormal(
                self.mesh_name,
                normalMode=2,
                userNormalMode=0,
                constructionHistory=False
            )

    def _set_hard_edges(self) -> None:
        """すべてのエッジをハードエッジに設定します."""
        if self.mesh_name:
            cmds.polySoftEdge(
                self.mesh_name,
                angle=0,
                constructionHistory=False
            )

    def apply_waveform(self, params: Dict[str, Any]) -> None:
        """polyPlaneの頂点へ波形を適用します.

        Args:
            params: パラメータ辞書.
        """
        unit_len: float = self.unit_length(params)
        units: int = int(params.get(BaseWaveParamKey.UNITS, BaseWaveConstants.DEFAULT_UNITS))
        total_len: float = unit_len * units

        all_xy: List[Tuple[float, float]] = self._build_xy_coordinates(params)

        unit_pts: List[Tuple[float, float]] = self.unit_points(params)
        sx: int = units * (len(unit_pts) - 1)
        num_x_verts: int = sx + 1

        self._apply_coordinates_to_mesh(all_xy, total_len, num_x_verts)

    def create_polygon(self, params: Dict[str, Any]) -> str:
        """ポリゴンを作成/更新します.

        Args:
            params: パラメータ辞書.

        Returns:
            生成されたメッシュの名前.
        """
        if self._should_rebuild(params):
            transform: Optional[Dict[str, List[float]]] = self._save_transform()
            self._delete_existing_mesh()
            self.mesh_name = self._create_base_plane(params)
            self._restore_transform(transform)
            self._update_last_params(params)

        self.apply_waveform(params)
        self._flip_normals()
        self._set_hard_edges()

        return self.mesh_name

    def _should_rebuild(self, params: Dict[str, Any]) -> bool:
        """メッシュを再構築する必要があるか判定します.

        Args:
            params: パラメータ辞書.

        Returns:
            再構築が必要な場合True.
        """
        return (
            not self.mesh_name or
            not cmds.objExists(self.mesh_name) or
            self._needs_rebuild(params)
        )

    def _update_last_params(self, params: Dict[str, Any]) -> None:
        """最後のパラメータを更新します.

        Args:
            params: パラメータ辞書.
        """
        self._last_params = params.copy()
        self._last_params[BaseWaveParamKey.DEPTH] = params.get(
            BaseWaveParamKey.DEPTH,
            BaseWaveConstants.DEFAULT_DEPTH
        )