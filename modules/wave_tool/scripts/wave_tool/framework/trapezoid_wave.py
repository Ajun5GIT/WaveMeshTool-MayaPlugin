"""台形波メッシュ生成モジュール."""
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from numpy.typing import NDArray
from maya import cmds
from wave_tool.framework.base_wave import BaseWave, BaseWaveParamKey, BaseWaveConstants


class TrapezoidWaveParamKey:
    """台形波のパラメータキー定数."""
    DIVISIONS_PER_UNIT: str = "divisions_per_unit"
    FLAT_TOP_WIDTH: str = "flat_top_width"
    EDGE_CURVATURE: str = "edge_curvature"
    SPAN: str = "span"
    CENTER: str = "center"
    CLOSE_END: str = "close_end"


class TrapezoidWaveConstants:
    """台形波の定数."""
    DEFAULT_WIDTH: float = 3.0
    DEFAULT_DIVISIONS_PER_UNIT: int = 20
    DEFAULT_FLAT_TOP_WIDTH: float = 0.0
    DEFAULT_EDGE_CURVATURE: float = 0.5
    DEFAULT_SPAN: float = 1.0
    DEFAULT_CENTER: float = 0.5
    DEFAULT_CLOSE_END: bool = False
    DEFAULT_UNITS: int = 3

    MIN_DIVISIONS: int = 2
    MIN_CURVATURE: float = 1e-6
    DENSE_MULTIPLIER: int = 40
    MIN_DENSE_SAMPLES: int = 200
    MERGE_VERTEX_DISTANCE: float = 0.001
    DEFAULT_NUM_PREVIEW_POINTS: int = 100


class TrapezoidWave(BaseWave):
    """台形波メッシュ生成クラス."""

    name: str = "trapezoid"

    def unit_points(self, params: Dict[str, Any]) -> List[Tuple[float, float]]:
        """1ユニット分の2D点列を等弧長サンプリングで生成します.

        Args:
            params: パラメータ辞書

        Returns:
            (x, y)座標のリスト
        """
        width = float(params.get(BaseWaveParamKey.WIDTH, TrapezoidWaveConstants.DEFAULT_WIDTH))
        height = float(params.get(BaseWaveParamKey.HEIGHT, BaseWaveConstants.DEFAULT_HEIGHT))
        divisions = max(
            TrapezoidWaveConstants.MIN_DIVISIONS,
            int(params.get(TrapezoidWaveParamKey.DIVISIONS_PER_UNIT, TrapezoidWaveConstants.DEFAULT_DIVISIONS_PER_UNIT))
        )
        xs, ys = self._calculate_equal_chord_polyline(width, height, divisions, params)
        return list(zip(xs, ys))

    def unit_length(self, params: Dict[str, Any]) -> float:
        """1ユニットの長さ(X方向)を返します.

        Args:
            params: パラメータ辞書

        Returns:
            ユニットの長さ
        """
        return float(params.get(BaseWaveParamKey.WIDTH, TrapezoidWaveConstants.DEFAULT_WIDTH))

    def _needs_rebuild(self, params: Dict[str, Any]) -> bool:
        """メッシュ再構築が必要か判定します.

        Args:
            params: パラメータ辞書

        Returns:
            再構築が必要な場合True
        """
        if not self._last_params:
            return True

        critical_params = [
            BaseWaveParamKey.UNITS,
            BaseWaveParamKey.DEPTH,
            TrapezoidWaveParamKey.DIVISIONS_PER_UNIT,
            BaseWaveParamKey.WIDTH,
            BaseWaveParamKey.HEIGHT,
            TrapezoidWaveParamKey.FLAT_TOP_WIDTH,
            TrapezoidWaveParamKey.EDGE_CURVATURE
        ]

        for key in critical_params:
            if params.get(key) != self._last_params.get(key):
                return True

        return False

    def _calculate_equal_chord_polyline(
            self,
            width: float,
            height: float,
            divisions: int,
            params: Dict[str, Any]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """等弧長ポリラインを計算します.

        Args:
            width: 幅
            height: 高さ
            divisions: 分割数
            params: パラメータ辞書

        Returns:
            x座標配列とy座標配列のタプル
        """
        dense = max(TrapezoidWaveConstants.MIN_DENSE_SAMPLES, divisions * TrapezoidWaveConstants.DENSE_MULTIPLIER)
        t_dense = np.linspace(0.0, 1.0, dense + 1)
        y01 = np.array([self._evaluate_trapezoid(t, params) for t in t_dense], dtype=float)
        x_dense = t_dense * width
        y_dense = y01 * height

        dx = np.diff(x_dense)
        dy = np.diff(y_dense)
        seg_len = np.hypot(dx, dy)

        s = np.empty(dense + 1, dtype=float)
        s[0] = 0.0
        s[1:] = np.cumsum(seg_len)
        total = s[-1] if s[-1] > 0 else 1.0

        s_targets = np.linspace(0.0, total, divisions + 1)
        t_eq = np.interp(s_targets, s, t_dense)
        x_eq = t_eq * width
        y_eq = np.array([self._evaluate_trapezoid(t, params) for t in t_eq]) * height
        return x_eq, y_eq

    def _evaluate_trapezoid(self, x01: float, params: Dict[str, Any]) -> float:
        """台形波関数を評価します(0..1 → 0..1).

        Args:
            x01: 入力値(0から1の範囲)
            params: パラメータ辞書

        Returns:
            台形波の出力値(0から1の範囲)
        """
        x = float(np.clip(x01, 0.0, 1.0))
        top = float(np.clip(
            params.get(TrapezoidWaveParamKey.FLAT_TOP_WIDTH, TrapezoidWaveConstants.DEFAULT_FLAT_TOP_WIDTH),
            0.0,
            1.0
        ))
        k = max(
            TrapezoidWaveConstants.MIN_CURVATURE,
            float(params.get(TrapezoidWaveParamKey.EDGE_CURVATURE, TrapezoidWaveConstants.DEFAULT_EDGE_CURVATURE))
        )

        span = float(np.clip(
            params.get(TrapezoidWaveParamKey.SPAN, TrapezoidWaveConstants.DEFAULT_SPAN),
            0.0,
            1.0
        ))
        center = float(params.get(TrapezoidWaveParamKey.CENTER, TrapezoidWaveConstants.DEFAULT_CENTER))
        half = span * 0.5
        center = float(np.clip(center, half, 1.0 - half))

        a = center - half
        d = center + half
        total = d - a
        flat_span = total * top
        edge_width = (total - flat_span) * 0.5

        b = a + edge_width
        c = d - edge_width

        if x < a:
            return 0.0
        elif x < b:
            t = 0.0 if edge_width == 0.0 else (x - a) / edge_width
            return float(self._calculate_smooth_edge_curve(t, k))
        elif x < c:
            return 1.0
        elif x < d:
            t = 0.0 if edge_width == 0.0 else (x - c) / edge_width
            return float(self._calculate_smooth_edge_curve(1.0 - t, k))
        else:
            return 0.0

    @staticmethod
    def _calculate_smooth_edge_curve(t: float, k: float) -> float:
        """滑らかなエッジ曲線を計算します.

        Args:
            t: 入力値(0から1の範囲)
            k: 曲率パラメータ

        Returns:
            曲線の出力値
        """
        t = float(np.clip(t, 0.0, 1.0))
        k = max(TrapezoidWaveConstants.MIN_CURVATURE, float(k))
        s_pow = t ** k
        inv_pow = (1.0 - t) ** k
        s = s_pow / (s_pow + inv_pow)
        u = s * s * s * (s * (s * 6.0 - 15.0) + 10.0)
        return 0.5 - 0.5 * np.cos(np.pi * u)

    def _build_3d_mesh_directly(self, params: Dict[str, Any]) -> str:
        """3Dメッシュを直接構築します（台形波専用の実装）.

        Args:
            params: パラメータ辞書

        Returns:
            生成されたメッシュ名
        """
        width = float(params.get(BaseWaveParamKey.WIDTH, TrapezoidWaveConstants.DEFAULT_WIDTH))
        height = float(params.get(BaseWaveParamKey.HEIGHT, BaseWaveConstants.DEFAULT_HEIGHT))
        depth = float(params.get(BaseWaveParamKey.DEPTH, BaseWaveConstants.DEFAULT_DEPTH))
        units = int(params.get(BaseWaveParamKey.UNITS, TrapezoidWaveConstants.DEFAULT_UNITS))
        divisions = max(
            TrapezoidWaveConstants.MIN_DIVISIONS,
            int(params.get(TrapezoidWaveParamKey.DIVISIONS_PER_UNIT, TrapezoidWaveConstants.DEFAULT_DIVISIONS_PER_UNIT))
        )
        close_end = bool(params.get(TrapezoidWaveParamKey.CLOSE_END, TrapezoidWaveConstants.DEFAULT_CLOSE_END))

        zf, zb = depth * 0.5, -depth * 0.5
        front_pts: List[Tuple[float, float, float]] = []
        back_pts: List[Tuple[float, float, float]] = []

        xs_unit, ys_unit = self._calculate_equal_chord_polyline(width, height, divisions, params)

        for u in range(units):
            offset = u * width
            start_j = 0 if u == 0 else 1
            for j in range(start_j, len(xs_unit)):
                x = xs_unit[j] + offset
                y = ys_unit[j]
                front_pts.append((x, y, zf))
                back_pts.append((x, y, zb))

        mesh_name = self._create_mesh_from_points(front_pts, back_pts, close_end)
        return mesh_name

    def _create_mesh_from_points(
            self,
            front_pts: List[Tuple[float, float, float]],
            back_pts: List[Tuple[float, float, float]],
            close_end: bool
    ) -> Optional[str]:
        """点列からメッシュを作成します.

        Args:
            front_pts: 前面の点リスト
            back_pts: 背面の点リスト
            close_end: 端を閉じるか

        Returns:
            生成されたメッシュ名
        """
        segs = len(front_pts) - 1
        if segs <= 0:
            return None

        quad_meshes = self._create_quad_segments(front_pts, back_pts, segs)
        mesh = self._unite_segments(quad_meshes)

        if close_end:
            cmds.polyCloseBorder(mesh, ch=0)

        self._merge_vertices(mesh)
        self._center_pivot(mesh)

        return mesh

    def _create_quad_segments(
            self,
            front_pts: List[Tuple[float, float, float]],
            back_pts: List[Tuple[float, float, float]],
            segs: int
    ) -> List[str]:
        """四角形セグメントを作成します.

        Args:
            front_pts: 前面の点リスト
            back_pts: 背面の点リスト
            segs: セグメント数

        Returns:
            作成されたメッシュのリスト
        """
        quad_meshes = []
        for i in range(segs):
            p0 = front_pts[i]
            p1 = front_pts[i + 1]
            p2 = back_pts[i + 1]
            p3 = back_pts[i]
            m = cmds.polyCreateFacet(p=[p0, p1, p2, p3], n=f"temp_seg_{i}")[0]
            quad_meshes.append(m)
        return quad_meshes

    def _unite_segments(self, quad_meshes: List[str]) -> str:
        """セグメントを結合します.

        Args:
            quad_meshes: 結合するメッシュのリスト

        Returns:
            結合されたメッシュ名
        """
        if len(quad_meshes) == 1:
            return cmds.rename(quad_meshes[0], self.name)

        mesh = cmds.polyUnite(quad_meshes, ch=0, mergeUVSets=1, n=self.name)[0]
        try:
            cmds.delete(quad_meshes)
        except Exception:
            pass

        return mesh

    def _merge_vertices(self, mesh: str) -> None:
        """頂点をマージします.

        Args:
            mesh: メッシュ名
        """
        try:
            cmds.polyMergeVertex(mesh, d=TrapezoidWaveConstants.MERGE_VERTEX_DISTANCE)
        except Exception:
            pass

    def _center_pivot(self, mesh: str) -> None:
        """ピボットを中心に配置します.

        Args:
            mesh: メッシュ名
        """
        cmds.xform(mesh, cp=1)

    def create_polygon(self, params: Dict[str, Any]) -> str:
        """ポリゴンメッシュを生成します.

        Args:
            params: パラメータ辞書

        Returns:
            生成されたメッシュの名前
        """
        if self._should_rebuild(params):
            transform = self._save_transform()
            self._delete_existing_mesh()
            self.mesh_name = self._build_3d_mesh_directly(params)
            self._restore_transform(transform)
            self._flip_normals()
            self._update_last_params(params)

        return self.mesh_name

    def get_preview_curve(
            self,
            params: Dict[str, Any],
            num_points: int = TrapezoidWaveConstants.DEFAULT_NUM_PREVIEW_POINTS
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """プレビュー用の高精細カーブを取得します.

        Args:
            params: パラメータ辞書
            num_points: ポイント数

        Returns:
            x座標配列とy座標配列のタプル
        """
        width = float(params.get(BaseWaveParamKey.WIDTH, TrapezoidWaveConstants.DEFAULT_WIDTH))
        height = float(params.get(BaseWaveParamKey.HEIGHT, BaseWaveConstants.DEFAULT_HEIGHT))
        xs, ys = self._calculate_equal_chord_polyline(
            width,
            height,
            max(TrapezoidWaveConstants.MIN_DIVISIONS, num_points - 1),
            params
        )
        return np.asarray(xs), np.asarray(ys)