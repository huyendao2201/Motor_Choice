import sys
sys.path.insert(0, '.')
from ai_engine import generate_training_data, AHPWeightPredictor, DSSEngine
import pandas as pd
import os

print("=== TEST: Full pipeline ===")
X, y = generate_training_data(300)
predictor = AHPWeightPredictor()
metrics = predictor.train(X, y)
print("Model MAE:", round(metrics['mae'],4), "RMSE:", round(metrics['rmse'],4))

os.makedirs('../models', exist_ok=True)
predictor.save('../models/ahp_model.joblib')
print("Model saved!")

df = pd.read_excel('data/data.xlsx')
dss = DSSEngine(df)
print("Dataset:", len(df), "bikes, brands:", df['brand'].nunique())

# Test sinh vien
user = {'budget':25,'purpose':0,'vehicle_type_preference':0,'daily_distance_km':15,
        'priority_price':0.35,'priority_fuel':0.30,'priority_performance':0.15,
        'priority_design':0.10,'priority_brand':0.10}
weights = predictor.predict_weights(user)
print("Weights:", {k:round(v,3) for k,v in weights.items()}, "| Sum=", round(sum(weights.values()),3))

filtered = dss.filter_motorcycles(max_budget=25, vehicle_type='Xe số')
if filtered.empty:
    filtered = dss.filter_motorcycles(max_budget=30)
ranked = dss.rank_motorcycles(weights, filtered)
print("TOP 5 (Sinh vien):")
for _,r in ranked.head(5).iterrows():
    print("  #" + str(r['rank']) + " " + str(r['brand']) + " " + str(r['model']) + " - " + str(r['price_million_vnd']) + "M - Score:" + str(round(r['total_score'],4)))

# Test van phong
user2 = {'budget':70,'purpose':1,'vehicle_type_preference':1,'daily_distance_km':20,
         'priority_price':0.10,'priority_fuel':0.10,'priority_performance':0.20,
         'priority_design':0.30,'priority_brand':0.30}
weights2 = predictor.predict_weights(user2)
print("Weights (van phong):", {k:round(v,3) for k,v in weights2.items()})
filtered2 = dss.filter_motorcycles(max_budget=70, vehicle_type='Xe tay ga')
if filtered2.empty:
    filtered2 = dss.filter_motorcycles(vehicle_type='Xe tay ga')
ranked2 = dss.rank_motorcycles(weights2, filtered2)
print("TOP 5 (Van phong):")
for _,r in ranked2.head(5).iterrows():
    print("  #" + str(r['rank']) + " " + str(r['brand']) + " " + str(r['model']) + " - " + str(r['price_million_vnd']) + "M - Score:" + str(round(r['total_score'],4)))

print("ALL TESTS PASSED!")
