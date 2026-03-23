"""
DSS Motor Choice - AI Engine Module
Multi-output Random Forest Regressor để dự đoán trọng số AHP
Phiên bản nâng cao: Validation chặt chẽ, logging, error handling tốt hơn
"""

import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
from typing import Dict, List, Optional, Tuple

# ============================================================
# LOGGING SETUP
# ============================================================
logger = logging.getLogger("DSS.AIEngine")


# ============================================================
# CONSTANTS
# ============================================================
WEIGHT_NAMES = ['w_price', 'w_fuel', 'w_performance', 'w_design', 'w_brand']
FEATURE_NAMES = [
    'budget', 'purpose', 'vehicle_type_preference', 'daily_distance_km',
    'priority_price', 'priority_fuel', 'priority_performance',
    'priority_design', 'priority_brand'
]
CRITERIA = {
    'price_million_vnd': 'cost',
    'fuel_consumption_l_per_100km': 'cost',
    'performance_score': 'benefit',
    'design_score': 'benefit',
    'brand_score': 'benefit'
}
CRITERIA_COLS = list(CRITERIA.keys())


# ============================================================
# 1. TẠO DỮ LIỆU TRAIN GIẢ LẬP (300 mẫu)
# ============================================================

def generate_training_data(n_samples: int = 300, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Tạo dữ liệu huấn luyện giả lập với 4 nhóm người dùng:
    - Sinh viên: ưu tiên giá và tiết kiệm xăng
    - Nhân viên văn phòng: ưu tiên thiết kế và thương hiệu
    - Người đi tour: ưu tiên hiệu năng
    - Người chạy dịch vụ: ưu tiên tiết kiệm xăng và giá

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (features X, targets y)
    """
    np.random.seed(random_state)

    profiles = []
    weights_list = []
    n_per_group = n_samples // 4

    # ---- Nhóm Sinh viên (purpose=0) ----
    for _ in range(n_per_group):
        budget = np.random.randint(15, 35)
        daily_km = np.random.randint(5, 20)
        p_price = np.random.uniform(0.25, 0.40)
        p_fuel = np.random.uniform(0.20, 0.35)
        p_perf = np.random.uniform(0.10, 0.20)
        p_design = np.random.uniform(0.05, 0.15)
        p_brand = np.random.uniform(0.05, 0.15)

        profiles.append({
            'budget': budget, 'purpose': 0, 'vehicle_type_preference': 0,
            'daily_distance_km': daily_km,
            'priority_price': p_price, 'priority_fuel': p_fuel,
            'priority_performance': p_perf, 'priority_design': p_design, 'priority_brand': p_brand
        })
        raw = np.array([p_price, p_fuel, p_perf, p_design, p_brand])
        weights_list.append(raw / raw.sum())

    # ---- Nhóm Nhân viên văn phòng (purpose=1) ----
    for _ in range(n_per_group):
        budget = np.random.randint(40, 100)
        daily_km = np.random.randint(10, 30)
        p_price = np.random.uniform(0.10, 0.20)
        p_fuel = np.random.uniform(0.10, 0.20)
        p_perf = np.random.uniform(0.15, 0.25)
        p_design = np.random.uniform(0.25, 0.35)
        p_brand = np.random.uniform(0.20, 0.30)

        profiles.append({
            'budget': budget, 'purpose': 1, 'vehicle_type_preference': 1,
            'daily_distance_km': daily_km,
            'priority_price': p_price, 'priority_fuel': p_fuel,
            'priority_performance': p_perf, 'priority_design': p_design, 'priority_brand': p_brand
        })
        raw = np.array([p_price, p_fuel, p_perf, p_design, p_brand])
        weights_list.append(raw / raw.sum())

    # ---- Nhóm Người đi tour (purpose=2) ----
    for _ in range(n_per_group):
        budget = np.random.randint(40, 120)
        daily_km = np.random.randint(50, 150)
        p_price = np.random.uniform(0.10, 0.20)
        p_fuel = np.random.uniform(0.10, 0.20)
        p_perf = np.random.uniform(0.35, 0.50)
        p_design = np.random.uniform(0.10, 0.20)
        p_brand = np.random.uniform(0.10, 0.20)

        profiles.append({
            'budget': budget, 'purpose': 2, 'vehicle_type_preference': 2,
            'daily_distance_km': daily_km,
            'priority_price': p_price, 'priority_fuel': p_fuel,
            'priority_performance': p_perf, 'priority_design': p_design, 'priority_brand': p_brand
        })
        raw = np.array([p_price, p_fuel, p_perf, p_design, p_brand])
        weights_list.append(raw / raw.sum())

    # ---- Nhóm Người chạy dịch vụ (purpose=3) ----
    for _ in range(n_samples - 3 * n_per_group):
        budget = np.random.randint(20, 50)
        daily_km = np.random.randint(80, 200)
        p_price = np.random.uniform(0.20, 0.30)
        p_fuel = np.random.uniform(0.30, 0.45)
        p_perf = np.random.uniform(0.10, 0.20)
        p_design = np.random.uniform(0.05, 0.10)
        p_brand = np.random.uniform(0.05, 0.10)

        profiles.append({
            'budget': budget, 'purpose': 3, 'vehicle_type_preference': 0,
            'daily_distance_km': daily_km,
            'priority_price': p_price, 'priority_fuel': p_fuel,
            'priority_performance': p_perf, 'priority_design': p_design, 'priority_brand': p_brand
        })
        raw = np.array([p_price, p_fuel, p_perf, p_design, p_brand])
        weights_list.append(raw / raw.sum())

    df_X = pd.DataFrame(profiles)
    df_y = pd.DataFrame(weights_list, columns=WEIGHT_NAMES)

    # Validate: tổng trọng số mỗi hàng phải xấp xỉ 1
    row_sums = df_y.sum(axis=1)
    assert (row_sums - 1.0).abs().max() < 1e-8, "Training data weights do not sum to 1!"

    logger.info(f"✅ Generated {len(df_X)} training samples for 4 user groups.")
    return df_X, df_y


# ============================================================
# 2. HUẤN LUYỆN MÔ HÌNH RANDOM FOREST
# ============================================================

class AHPWeightPredictor:
    """Multi-output Random Forest để dự đoán trọng số AHP từ user profile."""

    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.feature_names = FEATURE_NAMES
        self.weight_names = WEIGHT_NAMES
        self.is_trained = False
        self.eval_metrics: Dict = {}

    def _validate_features(self, user_profile: dict) -> None:
        """Kiểm tra các feature bắt buộc tồn tại trong user_profile."""
        missing = [f for f in self.feature_names if f not in user_profile]
        if missing:
            raise ValueError(f"Thiếu các trường bắt buộc: {missing}")

        # Validate ranges
        if not (10 <= user_profile.get('budget', 0) <= 500):
            raise ValueError("Budget phải trong khoảng 10–500 triệu VNĐ")
        if user_profile.get('purpose') not in [0, 1, 2, 3]:
            raise ValueError("Purpose phải là 0, 1, 2 hoặc 3")
        if user_profile.get('vehicle_type_preference') not in [0, 1, 2, 3]:
            raise ValueError("vehicle_type_preference phải là 0–3")
        for p_key in ['priority_price', 'priority_fuel', 'priority_performance', 'priority_design', 'priority_brand']:
            v = user_profile.get(p_key, -1)
            if not (0 <= v <= 1):
                raise ValueError(f"{p_key} phải trong khoảng 0–1, nhận được: {v}")

    def train(self, X: pd.DataFrame, y: pd.DataFrame) -> Dict:
        """Huấn luyện mô hình với train/test split 80/20."""
        if X.empty or y.empty:
            raise ValueError("Dữ liệu training không được rỗng")
        if len(X) != len(y):
            raise ValueError("X và y phải có cùng số dòng")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)

        # Validate predictions sum to ~1
        pred_sums = y_pred.sum(axis=1)
        logger.info(f"Prediction sums – min: {pred_sums.min():.4f}, max: {pred_sums.max():.4f}")

        self.eval_metrics = {
            'mae': round(float(mean_absolute_error(y_test, y_pred)), 6),
            'mse': round(float(mean_squared_error(y_test, y_pred)), 6),
            'rmse': round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 6),
            'r2_approx': round(float(1 - mean_squared_error(y_test, y_pred) / y_test.values.var()), 4),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test))
        }

        logger.info(f"✅ RF trained | MAE={self.eval_metrics['mae']:.4f} | RMSE={self.eval_metrics['rmse']:.4f}")
        return self.eval_metrics

    def predict_weights(self, user_profile: dict) -> Dict[str, float]:
        """
        Dự đoán trọng số AHP từ user profile.
        Luôn normalize lại để tổng = 1.

        Args:
            user_profile: dict chứa các feature name và giá trị
        Returns:
            Dict[str, float]: trọng số AHP (tổng = 1.0)
        Raises:
            RuntimeError: nếu model chưa được train
            ValueError: nếu user_profile thiếu fields
        """
        if not self.is_trained:
            raise RuntimeError("Model chưa được huấn luyện! Gọi train() trước.")

        self._validate_features(user_profile)

        X = pd.DataFrame([user_profile], columns=self.feature_names)
        raw_weights = self.model.predict(X)[0]

        # Clip âm về 0 (Random Forest đôi khi predict âm nhỏ)
        raw_weights = np.clip(raw_weights, 0, None)

        # Đảm bảo không bị zero-division
        total = raw_weights.sum()
        if total <= 0:
            logger.warning("Predicted weights are all zero/negative! Using equal weights.")
            normalized = np.ones(len(WEIGHT_NAMES)) / len(WEIGHT_NAMES)
        else:
            normalized = raw_weights / total

        # Final sanity check
        assert abs(normalized.sum() - 1.0) < 1e-6, f"Weights không tổng bằng 1: {normalized.sum()}"

        result = dict(zip(self.weight_names, normalized.tolist()))
        logger.debug(f"Predicted weights: { {k: round(v,3) for k,v in result.items()} }")
        return result

    def get_feature_importance(self) -> Dict[str, float]:
        """Trả về feature importance của model."""
        if not self.is_trained:
            return {}
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, [round(float(v), 4) for v in importance]))

    def save(self, path: str) -> None:
        """Lưu model xuống file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"✅ Model saved to {path}")

    @staticmethod
    def load(path: str) -> 'AHPWeightPredictor':
        """Load model từ file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file không tồn tại: {path}")
        predictor = joblib.load(path)
        if not isinstance(predictor, AHPWeightPredictor):
            raise TypeError("File không phải là AHPWeightPredictor!")
        logger.info(f"✅ Model loaded from {path}")
        return predictor


# ============================================================
# 3. DSS ENGINE - CHUẨN HÓA & XẾP HẠNG
# ============================================================

class DSSEngine:
    """
    Decision Support System Engine
    Chuẩn hóa dữ liệu xe và xếp hạng dựa trên trọng số AHP.

    Thuật toán:
    - Cost criteria: norm = (max - x) / (max - min)
    - Benefit criteria: norm = (x - min) / (max - min)
    - Score(i) = Σ wj * norm(xij)
    """

    CRITERIA = CRITERIA

    def __init__(self, motorcycles_df: pd.DataFrame):
        self._validate_dataset(motorcycles_df)
        self.df = motorcycles_df.copy()
        self._precompute_ranges()
        logger.info(f"✅ DSSEngine initialized with {len(self.df)} motorcycles.")

    def _validate_dataset(self, df: pd.DataFrame) -> None:
        """Kiểm tra dataset có đủ cột cần thiết."""
        required_cols = ['brand', 'model', 'vehicle_type', 'engine_cc',
                         'price_million_vnd', 'fuel_consumption_l_per_100km',
                         'performance_score', 'design_score', 'brand_score']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Dataset thiếu các cột: {missing}")
        if df.empty:
            raise ValueError("Dataset rỗng!")
        if df[CRITERIA_COLS].isnull().any().any():
            null_counts = df[CRITERIA_COLS].isnull().sum()
            logger.warning(f"Dataset có giá trị null:\n{null_counts[null_counts > 0]}")

    def _precompute_ranges(self) -> None:
        """Tính min/max toàn bộ dataset cho các tiêu chí."""
        self.ranges: Dict[str, Dict[str, float]] = {}
        for col in self.CRITERIA:
            col_data = self.df[col].dropna()
            if col_data.empty:
                raise ValueError(f"Cột {col} không có dữ liệu hợp lệ")
            self.ranges[col] = {
                'min': float(col_data.min()),
                'max': float(col_data.max())
            }
        logger.debug(f"Precomputed ranges: {self.ranges}")

    def normalize(self, value: float, col: str) -> float:
        """
        Chuẩn hóa theo loại tiêu chí (cost/benefit).

        Args:
            value: Giá trị cần chuẩn hóa
            col: Tên cột tiêu chí
        Returns:
            float: Giá trị chuẩn hóa [0, 1]
        """
        if col not in self.CRITERIA:
            raise ValueError(f"Cột '{col}' không phải tiêu chí hợp lệ")

        mn = self.ranges[col]['min']
        mx = self.ranges[col]['max']

        if mx == mn:
            return 1.0  # Tất cả giá trị bằng nhau → normalize = 1

        if self.CRITERIA[col] == 'cost':
            return max(0.0, min(1.0, (mx - value) / (mx - mn)))
        else:
            return max(0.0, min(1.0, (value - mn) / (mx - mn)))

    def filter_motorcycles(
        self,
        max_budget: Optional[float] = None,
        vehicle_type: Optional[str] = None,
        min_engine_cc: Optional[int] = None,
        max_engine_cc: Optional[int] = None,
        brands: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Lọc xe theo điều kiện người dùng.

        Returns:
            pd.DataFrame: DataFrame các xe phù hợp
        """
        df = self.df.copy()

        if max_budget is not None:
            if max_budget <= 0:
                raise ValueError("max_budget phải > 0")
            df = df[df['price_million_vnd'] <= max_budget]

        if vehicle_type and vehicle_type != 'Tất cả':
            valid_types = ['Xe số', 'Xe tay ga', 'Xe côn tay']
            if vehicle_type not in valid_types:
                raise ValueError(f"vehicle_type phải là một trong {valid_types}")
            df = df[df['vehicle_type'] == vehicle_type]

        if min_engine_cc is not None:
            df = df[df['engine_cc'] >= min_engine_cc]

        if max_engine_cc is not None:
            df = df[df['engine_cc'] <= max_engine_cc]

        if brands:
            df = df[df['brand'].isin(brands)]

        return df.reset_index(drop=True)

    def rank_motorcycles(
        self,
        weights: Dict[str, float],
        filtered_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Tính điểm AHP và xếp hạng xe.
        Score(i) = Σ wj * norm(xij)

        Args:
            weights: Dict trọng số AHP (tổng phải = 1)
            filtered_df: DataFrame đã lọc (nếu None, dùng toàn bộ dataset)
        Returns:
            pd.DataFrame: Xe đã xếp hạng (kèm cột total_score, rank, norm_*)
        Raises:
            ValueError: nếu weights không hợp lệ
        """
        # Validate weights
        self._validate_weights(weights)

        df = (filtered_df if filtered_df is not None else self.df).copy()
        if df.empty:
            logger.warning("Không có xe nào để xếp hạng!")
            return df

        weight_map = {
            'price_million_vnd': weights.get('w_price', 0.2),
            'fuel_consumption_l_per_100km': weights.get('w_fuel', 0.2),
            'performance_score': weights.get('w_performance', 0.2),
            'design_score': weights.get('w_design', 0.2),
            'brand_score': weights.get('w_brand', 0.2),
        }

        # Tính norm scores
        for col in self.CRITERIA:
            df[f'norm_{col}'] = df[col].apply(lambda v: self.normalize(v, col))

        # Tính tổng điểm
        df['total_score'] = sum(
            weight_map[col] * df[f'norm_{col}']
            for col in self.CRITERIA
        )

        # Validate tổng score hợp lý
        assert df['total_score'].between(0, 1).all(), "total_score vượt ngoài [0, 1]!"

        df = df.sort_values('total_score', ascending=False).reset_index(drop=True)
        df['rank'] = df.index + 1

        return df

    def _validate_weights(self, weights: Dict[str, float]) -> None:
        """Kiểm tra trọng số hợp lệ."""
        required_keys = ['w_price', 'w_fuel', 'w_performance', 'w_design', 'w_brand']
        missing = [k for k in required_keys if k not in weights]
        if missing:
            raise ValueError(f"Thiếu trọng số: {missing}")

        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:  # Cho phép sai số 1%
            raise ValueError(f"Tổng trọng số phải bằng 1, hiện tại: {total:.4f}")

        for k, v in weights.items():
            if v < 0:
                raise ValueError(f"Trọng số '{k}' không được âm: {v}")

    def explain_result(self, row: pd.Series, weights: Dict[str, float]) -> str:
        """Tạo giải thích tự nhiên cho kết quả xe đứng đầu."""
        weight_map = {
            'w_price': ('giá thành', row.get('norm_price_million_vnd', 0)),
            'w_fuel': ('tiết kiệm nhiên liệu', row.get('norm_fuel_consumption_l_per_100km', 0)),
            'w_performance': ('hiệu năng động cơ', row.get('norm_performance_score', 0)),
            'w_design': ('thiết kế ngoại thất', row.get('norm_design_score', 0)),
            'w_brand': ('uy tín thương hiệu', row.get('norm_brand_score', 0)),
        }

        # Đóng góp = trọng số × điểm chuẩn hóa
        contributions = {
            label: weights.get(k, 0) * score
            for k, (label, score) in weight_map.items()
        }
        top2 = sorted(contributions, key=contributions.get, reverse=True)[:2]

        brand = row.get('brand', '')
        model = row.get('model', '')
        price = row.get('price_million_vnd', 0)
        score = row.get('total_score', 0)

        return (
            f"**{brand} {model}** đạt điểm DSS cao nhất ({score:.3f}/1.000) "
            f"nhờ vượt trội về **{top2[0]}** và **{top2[1]}**. "
            f"Mức giá {price:.1f} triệu VNĐ phù hợp với tiêu chí đã đặt ra."
        )

    def get_statistics(self) -> Dict:
        """Thống kê tổng hợp dataset."""
        df = self.df
        return {
            "total": int(len(df)),
            "brands": df['brand'].value_counts().to_dict(),
            "vehicle_types": df['vehicle_type'].value_counts().to_dict(),
            "price_stats": {
                "min": round(float(df['price_million_vnd'].min()), 2),
                "max": round(float(df['price_million_vnd'].max()), 2),
                "mean": round(float(df['price_million_vnd'].mean()), 2),
                "median": round(float(df['price_million_vnd'].median()), 2),
            },
            "engine_cc_range": {
                "min": int(df['engine_cc'].min()),
                "max": int(df['engine_cc'].max()),
            },
            "score_stats": {
                col: {
                    "min": round(float(df[col].min()), 2),
                    "max": round(float(df[col].max()), 2),
                    "mean": round(float(df[col].mean()), 2),
                }
                for col in ['performance_score', 'design_score', 'brand_score']
            }
        }


# ============================================================
# 4. AHP PAIRWISE COMPARISON (Saaty scale)
# ============================================================

class AHPCalculator:
    """Tính toán AHP từ ma trận so sánh cặp (Saaty)."""

    RANDOM_INDEX = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}
    CRITERIA_NAMES = ['Giá', 'Xăng', 'Hiệu năng', 'Thiết kế', 'Thương hiệu']

    def compute_weights(self, matrix: List[List[float]], names: Optional[List[str]] = None) -> Dict:
        """
        Tính vector trọng số và Consistency Ratio từ ma trận so sánh cặp.

        Args:
            matrix: Ma trận vuông n×n (Saaty scale 1–9)
            names: Tên các phần tử để trả về trong dictionary
        Returns:
            dict: weights, lambda_max, CI, CR, is_consistent
        Raises:
            ValueError: nếu matrix không hợp lệ
        """
        A = np.array(matrix, dtype=float)
        n = A.shape[0]

        if names is None:
            if n == 5:
                names = self.CRITERIA_NAMES
            else:
                names = [f"Item {i+1}" for i in range(n)]

        # Validate
        if n < 2:
            raise ValueError("Ma trận phải có ít nhất 2 hàng/cột")
        if A.shape[0] != A.shape[1]:
            raise ValueError("Ma trận phải là ma trận vuông")
        if not np.all(A > 0):
            raise ValueError("Tất cả giá trị trong ma trận phải > 0")

        # Kiểm tra tính nhất quán cơ bản (aii = 1)
        for i in range(n):
            if abs(A[i, i] - 1.0) > 1e-6:
                raise ValueError(f"Giá trị đường chéo A[{i},{i}] phải bằng 1")

        # Chuẩn hóa cột
        col_sums = A.sum(axis=0)
        norm = A / col_sums

        # Vector trọng số = trung bình hàng
        w = norm.mean(axis=1)
        w = w / w.sum()  # Normalize lại

        # λ_max
        Aw = A @ w
        lambda_vals = Aw / w
        lambda_max = float(lambda_vals.mean())

        # Consistency Index & Ratio
        CI = (lambda_max - n) / (n - 1)
        RI = self.RANDOM_INDEX.get(n, 1.12)
        CR = CI / RI if RI > 0 else 0.0

        return {
            'weights': [round(float(x), 4) for x in w],
            'weights_named': dict(zip(names, [round(float(x), 4) for x in w])),
            'lambda_max': round(lambda_max, 4),
            'CI': round(CI, 4),
            'CR': round(CR, 4),
            'is_consistent': bool(n <= 2 or CR <= 0.1),
            'message': '✅ Ma trận nhất quán tốt (CR ≤ 0.1)' if (n <= 2 or CR <= 0.1) else f'⚠️ CR = {round(CR, 3)} > 0.1, cần xem lại ma trận',
            'details': {
                'names': names,
                'norm_matrix': norm.tolist(),
                'weighted_sum_value': Aw.tolist(),
                'consistency_vector': lambda_vals.tolist()
            }
        }


# ============================================================
# 5. KHỞI TẠO & QUẢN LÝ HỆ THỐNG
# ============================================================

_predictor: Optional[AHPWeightPredictor] = None
_dss_engine: Optional[DSSEngine] = None
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.normpath(os.path.join(_BASE_DIR, '..', 'models', 'ahp_model.joblib'))
DATA_PATH = os.path.join(_BASE_DIR, 'data', 'data.xlsx')


def initialize_system() -> Tuple[AHPWeightPredictor, DSSEngine]:
    """
    Khởi tạo AI model và DSS engine khi server start.
    Load model từ file nếu tồn tại, ngược lại train mới.

    Returns:
        Tuple[AHPWeightPredictor, DSSEngine]
    Raises:
        FileNotFoundError: nếu data.xlsx không tồn tại
    """
    global _predictor, _dss_engine

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Không tìm thấy dataset tại: {DATA_PATH}")

    # Load dataset
    logger.info(f"📊 Loading dataset from {DATA_PATH}...")
    df = pd.read_excel(DATA_PATH)
    if 'image_url' in df.columns:
        df['image_url'] = df['image_url'].fillna('')
        
    _dss_engine = DSSEngine(df)
    logger.info(f"✅ Loaded {len(df)} motorcycles.")

    # Load hoặc train model
    if os.path.exists(MODEL_PATH):
        try:
            _predictor = AHPWeightPredictor.load(MODEL_PATH)
            logger.info(f"✅ Model loaded. Metrics: {_predictor.eval_metrics}")
        except Exception as e:
            logger.warning(f"⚠️ Không thể load model: {e}. Đang train lại...")
            _predictor = _train_and_save()
    else:
        logger.info("⚙️  Đang huấn luyện mô hình Random Forest lần đầu...")
        _predictor = _train_and_save()

    return _predictor, _dss_engine


def _train_and_save() -> AHPWeightPredictor:
    """Train model mới và lưu."""
    X, y = generate_training_data(300)
    predictor = AHPWeightPredictor()
    metrics = predictor.train(X, y)
    predictor.save(MODEL_PATH)
    logger.info(f"✅ Model trained & saved. MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}")
    return predictor


def get_predictor() -> Optional[AHPWeightPredictor]:
    return _predictor


def get_dss_engine() -> Optional[DSSEngine]:
    return _dss_engine
