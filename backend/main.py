"""
DSS Motor Choice - FastAPI Backend (v2.0)
Cải thiện: Error handling chặt chẽ, logging, validation đầy đủ, CORS, docs
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, model_validator

from ai_engine import (
    AHPCalculator, AHPWeightPredictor, DSSEngine,
    generate_training_data, get_dss_engine, get_predictor, initialize_system,
    _train_and_save
)

# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("DSS.API")


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class UserProfile(BaseModel):
    budget: float = Field(..., ge=10, le=500, description="Ngân sách (triệu VNĐ)")
    purpose: int = Field(..., ge=0, le=3, description="0=Sinh viên, 1=Văn phòng, 2=Tour, 3=Dịch vụ")
    vehicle_type_preference: int = Field(..., ge=0, le=3, description="0=Xe số, 1=Tay ga, 2=Côn tay, 3=Tất cả")
    daily_distance_km: float = Field(..., ge=1, le=300, description="Khoảng cách đi hàng ngày (km)")
    priority_price: float = Field(..., ge=0, le=1, description="Mức độ ưu tiên giá (0–1)")
    priority_fuel: float = Field(..., ge=0, le=1, description="Mức độ ưu tiên tiết kiệm xăng (0–1)")
    priority_performance: float = Field(..., ge=0, le=1, description="Mức độ ưu tiên hiệu năng (0–1)")
    priority_design: float = Field(..., ge=0, le=1, description="Mức độ ưu tiên thiết kế (0–1)")
    priority_brand: float = Field(..., ge=0, le=1, description="Mức độ ưu tiên thương hiệu (0–1)")
    top_n: Optional[int] = Field(6, ge=1, le=20)
    min_engine_cc: Optional[int] = Field(None, ge=50, le=1000)
    max_engine_cc: Optional[int] = Field(None, ge=50, le=1000)
    brands: Optional[List[str]] = Field(None, description="Lọc theo thương hiệu cụ thể")

    @model_validator(mode='after')
    def validate_engine_cc_range(self) -> 'UserProfile':
        if self.min_engine_cc and self.max_engine_cc:
            if self.min_engine_cc > self.max_engine_cc:
                raise ValueError("min_engine_cc không được lớn hơn max_engine_cc")
        return self

    @model_validator(mode='after')
    def validate_priorities_not_all_zero(self) -> 'UserProfile':
        total = (self.priority_price + self.priority_fuel + self.priority_performance
                 + self.priority_design + self.priority_brand)
        if total <= 0:
            raise ValueError("Ít nhất một tiêu chí ưu tiên phải > 0")
        return self

    model_config = {"json_schema_extra": {
        "example": {
            "budget": 40, "purpose": 0, "vehicle_type_preference": 0,
            "daily_distance_km": 15, "priority_price": 0.35,
            "priority_fuel": 0.30, "priority_performance": 0.15,
            "priority_design": 0.10, "priority_brand": 0.10, "top_n": 6
        }
    }}


class AHPMatrixRequest(BaseModel):
    matrix: List[List[float]] = Field(..., description="Ma trận so sánh cặp NxN Saaty")
    names: Optional[List[str]] = Field(None, description="Danh sách tên các phần tử")

    @field_validator('matrix')
    @classmethod
    def validate_matrix_size(cls, v):
        n = len(v)
        if n < 2:
            raise ValueError("Ma trận phải có ít nhất 2 hàng")
        for row in v:
            if len(row) != n:
                raise ValueError(f"Mỗi hàng phải có đúng {n} phần tử")
            for val in row:
                if val <= 0:
                    raise ValueError("Tất cả giá trị trong ma trận phải > 0")
        return v


class RetrainRequest(BaseModel):
    n_samples: Optional[int] = Field(300, ge=100, le=2000)


class SensitivityRequest(BaseModel):
    """Tính lại ranking với trọng số tùy chỉnh (client-side DSS)."""
    weights: dict = Field(..., description="Dict trọng số {w_price, w_fuel, ...}")
    motorcycles: List[dict] = Field(..., description="Danh sách xe (có raw data)")

    @field_validator('weights')
    @classmethod
    def validate_weights_keys(cls, v):
        required = {'w_price', 'w_fuel', 'w_performance', 'w_design', 'w_brand'}
        missing = required - set(v.keys())
        if missing:
            raise ValueError(f"Thiếu trọng số: {missing}")
        for k, val in v.items():
            if val < 0:
                raise ValueError(f"Trọng số '{k}' không được âm")
        return v


# ============================================================
# LIFESPAN & APP SETUP
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management: khởi tạo khi start, cleanup khi stop."""
    logger.info("🚀 DSS Motor Choice API đang khởi động...")
    try:
        initialize_system()
        logger.info("✅ Hệ thống đã sẵn sàng!")
    except Exception as e:
        logger.critical(f"❌ CRITICAL: Không thể khởi tạo hệ thống: {e}")
        raise
    yield
    logger.info("🛑 DSS Motor Choice API đang tắt...")


app = FastAPI(
    title="Motor Choice DSS API",
    description="""
    ## 🏍️ Hệ thống Hỗ trợ Ra Quyết định Lựa chọn Xe máy

    Sử dụng **Random Forest AI** kết hợp **AHP** để đề xuất xe máy phù hợp nhất.

    ### Luồng hoạt động:
    1. Người dùng nhập thông tin cá nhân
    2. AI (Random Forest) dự đoán trọng số AHP
    3. Lọc xe theo ngân sách và loại
    4. Chuẩn hóa Min-Max theo tiêu chí Cost/Benefit
    5. Tính điểm tổng và xếp hạng
    6. Trả kết quả Top N + giải thích

    ### Tiêu chí AHP (5 tiêu chí):
    - 💰 Giá thành (Cost)
    - ⛽ Tiêu thụ nhiên liệu (Cost)
    - ⚡ Hiệu năng (Benefit)
    - 🎨 Thiết kế (Benefit)
    - 🏅 Thương hiệu (Benefit)
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MIDDLEWARE: Request logging & timing
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    response.headers["X-Process-Time-Ms"] = str(duration)
    return response


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Lỗi hệ thống nội bộ. Vui lòng thử lại.", "error": str(exc)}
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _get_system_or_raise():
    """Lấy predictor & dss_engine, raise 503 nếu chưa sẵn sàng."""
    predictor = get_predictor()
    dss = get_dss_engine()
    if not predictor or not dss:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hệ thống chưa sẵn sàng. Vui lòng thử lại sau vài giây."
        )
    return predictor, dss


VEHICLE_TYPE_MAP = {0: 'Xe số', 1: 'Xe tay ga', 2: 'Xe côn tay', 3: 'Tất cả'}
PURPOSE_LABELS = ["Sinh viên", "Nhân viên văn phòng", "Người đi tour", "Người chạy dịch vụ"]


# ============================================================
# ROUTES
# ============================================================

@app.get("/", tags=["System"], summary="API Info")
async def root():
    return {
        "name": "Motor Choice DSS API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "description": "Hệ thống hỗ trợ ra quyết định lựa chọn xe máy (AI + AHP + DSS)"
    }


@app.get("/api/health", tags=["System"], summary="Kiểm tra trạng thái hệ thống")
async def health_check():
    predictor = get_predictor()
    dss = get_dss_engine()
    is_ready = predictor is not None and dss is not None and predictor.is_trained

    return {
        "status": "ok" if is_ready else "initializing",
        "model_trained": predictor.is_trained if predictor else False,
        "motorcycles_loaded": len(dss.df) if dss else 0,
        "eval_metrics": predictor.eval_metrics if predictor else {},
        "feature_importance": predictor.get_feature_importance() if predictor and predictor.is_trained else {},
        "api_version": "2.0.0"
    }


@app.get("/api/motorcycles", tags=["Data"], summary="Danh sách tất cả xe máy")
async def get_all_motorcycles(
    vehicle_type: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Lấy danh sách xe máy, hỗ trợ lọc theo type/brand/price."""
    _, dss = _get_system_or_raise()

    df = dss.df.copy()

    if vehicle_type:
        df = df[df['vehicle_type'] == vehicle_type]
    if brand:
        df = df[df['brand'].str.lower() == brand.lower()]
    if min_price is not None:
        df = df[df['price_million_vnd'] >= min_price]
    if max_price is not None:
        df = df[df['price_million_vnd'] <= max_price]

    cols = ['brand', 'model', 'vehicle_type', 'engine_cc',
            'price_million_vnd', 'fuel_consumption_l_per_100km',
            'performance_score', 'design_score', 'brand_score']
    data = df[cols].to_dict('records')

    return {"motorcycles": data, "total": len(data), "filtered": any([vehicle_type, brand, min_price is not None, max_price is not None])}


@app.get("/api/motorcycles/stats", tags=["Data"], summary="Thống kê dataset xe máy")
async def get_statistics():
    _, dss = _get_system_or_raise()
    return dss.get_statistics()


@app.post("/api/recommend", tags=["DSS"], summary="🎯 Tư vấn xe máy – API chính")
async def recommend_motorcycles(profile: UserProfile):
    """
    **API chính**: Nhận user profile → AI dự đoán trọng số AHP → DSS xếp hạng xe.

    Quy trình:
    1. Validate input
    2. AI predict AHP weights (Random Forest)
    3. Filter bikes by budget/type/engine_cc
    4. Min-Max normalize criteria
    5. Score = Σ wj × norm(xij)
    6. Return Top N bikes + explanation
    """
    predictor, dss = _get_system_or_raise()

    user_dict = {
        'budget': profile.budget,
        'purpose': profile.purpose,
        'vehicle_type_preference': profile.vehicle_type_preference,
        'daily_distance_km': profile.daily_distance_km,
        'priority_price': profile.priority_price,
        'priority_fuel': profile.priority_fuel,
        'priority_performance': profile.priority_performance,
        'priority_design': profile.priority_design,
        'priority_brand': profile.priority_brand,
    }

    # 2. AI predict weights
    try:
        weights = predictor.predict_weights(user_dict)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=422, detail=f"Lỗi dự đoán AI: {str(e)}")

    # Sanity check on weights
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        logger.error(f"Predicted weights sum = {weight_sum}, expected 1.0!")
        raise HTTPException(status_code=500, detail="Lỗi nội bộ: trọng số AI không hợp lệ")

    # 3. Filter bikes
    vtype = VEHICLE_TYPE_MAP.get(profile.vehicle_type_preference, 'Tất cả')
    warning = None

    try:
        filtered_df = dss.filter_motorcycles(
            max_budget=profile.budget,
            vehicle_type=vtype if vtype != 'Tất cả' else None,
            min_engine_cc=profile.min_engine_cc,
            max_engine_cc=profile.max_engine_cc,
            brands=profile.brands
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if filtered_df.empty:
        # Fallback: bỏ filter budget, giữ loại xe
        filtered_df = dss.filter_motorcycles(
            vehicle_type=vtype if vtype != 'Tất cả' else None,
            brands=profile.brands
        )
        warning = (f"Không tìm thấy xe trong ngân sách {profile.budget}M VNĐ. "
                   f"Hiển thị {len(filtered_df)} xe phù hợp nhất với loại xe bạn chọn.")
        logger.info(f"Budget fallback triggered: {profile.budget}M → returned {len(filtered_df)} bikes")

    if filtered_df.empty:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy xe nào phù hợp với yêu cầu. Vui lòng điều chỉnh bộ lọc."
        )

    # 4. Rank
    try:
        ranked_df = dss.rank_motorcycles(weights, filtered_df)
    except (ValueError, AssertionError) as e:
        logger.error(f"Ranking error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi xếp hạng: {str(e)}")

    top_df = ranked_df.head(profile.top_n)

    # 5. Build result
    result_records = []
    for _, row in top_df.iterrows():
        result_records.append({
            'rank': int(row['rank']),
            'brand': str(row['brand']),
            'model': str(row['model']),
            'vehicle_type': str(row['vehicle_type']),
            'engine_cc': int(row['engine_cc']),
            'price_million_vnd': round(float(row['price_million_vnd']), 2),
            'fuel_consumption_l_per_100km': round(float(row['fuel_consumption_l_per_100km']), 2),
            'performance_score': round(float(row['performance_score']), 1),
            'design_score': round(float(row['design_score']), 1),
            'brand_score': round(float(row['brand_score']), 1),
            'total_score': round(float(row['total_score']), 4),
            'scores': {
                'price_norm': round(float(row.get('norm_price_million_vnd', 0)), 4),
                'fuel_norm': round(float(row.get('norm_fuel_consumption_l_per_100km', 0)), 4),
                'performance_norm': round(float(row.get('norm_performance_score', 0)), 4),
                'design_norm': round(float(row.get('norm_design_score', 0)), 4),
                'brand_norm': round(float(row.get('norm_brand_score', 0)), 4),
            }
        })

    # 6. Explanation
    explanation = ""
    if result_records:
        try:
            explanation = dss.explain_result(top_df.iloc[0], weights)
        except Exception as e:
            logger.warning(f"Could not generate explanation: {e}")
            explanation = "Không thể tạo giải thích tự động."

    # 7. Weight contributions
    weight_labels = {
        'w_price': {'label': '💰 Giá thành', 'type': 'cost', 'description': 'Càng thấp càng tốt'},
        'w_fuel': {'label': '⛽ Tiêu thụ xăng', 'type': 'cost', 'description': 'Càng thấp càng tốt'},
        'w_performance': {'label': '⚡ Hiệu năng', 'type': 'benefit', 'description': 'Càng cao càng tốt'},
        'w_design': {'label': '🎨 Thiết kế', 'type': 'benefit', 'description': 'Càng cao càng tốt'},
        'w_brand': {'label': '🏅 Thương hiệu', 'type': 'benefit', 'description': 'Càng cao càng tốt'},
    }

    criteria_contribution = {
        info['label']: {
            'weight': round(weights[k], 4),
            'weight_pct': round(weights[k] * 100, 1),
            'type': info['type'],
            'description': info['description']
        }
        for k, info in weight_labels.items()
    }

    return {
        "success": True,
        "ahp_weights": {k: round(v, 4) for k, v in weights.items()},
        "ahp_weights_pct": {k: round(v * 100, 1) for k, v in weights.items()},
        "criteria_contribution": criteria_contribution,
        "top_motorcycles": result_records,
        "explanation": explanation,
        "total_filtered": int(len(filtered_df)),
        "total_ranked": int(len(ranked_df)),
        "warning": warning,
        "user_profile_summary": {
            "purpose_label": PURPOSE_LABELS[profile.purpose],
            "vehicle_type_label": VEHICLE_TYPE_MAP[profile.vehicle_type_preference],
            "budget": profile.budget,
            "daily_km": profile.daily_distance_km,
        }
    }


@app.post("/api/ahp/calculate", tags=["AHP"], summary="Tính AHP từ ma trận so sánh cặp")
async def calculate_ahp(request: AHPMatrixRequest):
    """Tính trọng số AHP và Consistency Ratio từ ma trận Saaty NxN."""
    try:
        calculator = AHPCalculator()
        result = calculator.compute_weights(request.matrix, request.names)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"AHP calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán AHP: {str(e)}")


@app.get("/api/demo", tags=["Demo"], summary="Demo 2 người dùng mẫu")
async def run_demo():
    """Demo kết quả với Sinh viên và Nhân viên văn phòng."""
    predictor, dss = _get_system_or_raise()

    demo_profiles = [
        {
            "name": "Sinh viên – Nguyễn Văn A",
            "profile": {
                'budget': 25, 'purpose': 0, 'vehicle_type_preference': 0,
                'daily_distance_km': 15, 'priority_price': 0.35,
                'priority_fuel': 0.30, 'priority_performance': 0.15,
                'priority_design': 0.10, 'priority_brand': 0.10
            }
        },
        {
            "name": "Nhân viên văn phòng – Trần Thị B",
            "profile": {
                'budget': 70, 'purpose': 1, 'vehicle_type_preference': 1,
                'daily_distance_km': 20, 'priority_price': 0.10,
                'priority_fuel': 0.10, 'priority_performance': 0.20,
                'priority_design': 0.30, 'priority_brand': 0.30
            }
        }
    ]

    results = []
    for p in demo_profiles:
        weights = predictor.predict_weights(p['profile'])
        vtype = VEHICLE_TYPE_MAP.get(p['profile']['vehicle_type_preference'])
        filtered = dss.filter_motorcycles(
            max_budget=p['profile']['budget'],
            vehicle_type=vtype if vtype != 'Tất cả' else None
        )
        if filtered.empty:
            filtered = dss.filter_motorcycles(vehicle_type=vtype if vtype != 'Tất cả' else None)

        ranked = dss.rank_motorcycles(weights, filtered)
        top5 = ranked.head(5)

        results.append({
            'user': p['name'],
            'weights': {k: round(v, 3) for k, v in weights.items()},
            'top5': [
                {
                    'rank': int(row['rank']),
                    'brand': str(row['brand']),
                    'model': str(row['model']),
                    'price': round(float(row['price_million_vnd']), 1),
                    'score': round(float(row['total_score']), 4)
                }
                for _, row in top5.iterrows()
            ]
        })

    return {"demo_results": results, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}


@app.post("/api/retrain", tags=["Admin"], summary="Huấn luyện lại model AI")
async def retrain_model(request: RetrainRequest):
    """Huấn luyện lại Random Forest với số mẫu mới (100–2000)."""
    import ai_engine

    logger.info(f"🔄 Retraining model with {request.n_samples} samples...")
    try:
        X, y = generate_training_data(request.n_samples)
        new_predictor = AHPWeightPredictor()
        metrics = new_predictor.train(X, y)

        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'ahp_model.joblib')
        new_predictor.save(model_path)
        ai_engine._predictor = new_predictor

        logger.info(f"✅ Retrain complete. MAE={metrics['mae']}, RMSE={metrics['rmse']}")
        return {
            "success": True,
            "n_samples": request.n_samples,
            "metrics": metrics,
            "message": f"Model đã được huấn luyện lại với {request.n_samples} mẫu."
        }
    except Exception as e:
        logger.error(f"Retrain failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi huấn luyện: {str(e)}")


@app.post("/api/sensitivity/rank", tags=["DSS"], summary="Tính lại ranking với trọng số tùy chỉnh")
async def sensitivity_rank(request: SensitivityRequest):
    """
    Client-side DSS recalculation cho Sensitivity Analysis.
    Không gọi AI model – chỉ tính lại điểm với trọng số mới.
    """
    _, dss = _get_system_or_raise()

    # Normalize weights to sum = 1
    raw_weights = request.weights
    total = sum(raw_weights.values())
    if total <= 0:
        raise HTTPException(status_code=422, detail="Tổng trọng số phải > 0")

    normalized_weights = {k: v / total for k, v in raw_weights.items()}

    try:
        df = pd.DataFrame(request.motorcycles)
        ranked = dss.rank_motorcycles(normalized_weights, df)
        result = ranked[['brand', 'model', 'vehicle_type', 'price_million_vnd',
                          'total_score', 'rank']].head(10)
        return {
            "ranked": result.to_dict('records'),
            "weights_used": {k: round(v, 4) for k, v in normalized_weights.items()}
        }
    except Exception as e:
        logger.error(f"Sensitivity rank error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi tính toán: {str(e)}")
