from fastapi.testclient import TestClient
from src.s1_metrics.main import app
import json

client = TestClient(app)

print("🚀 Đang gửi request test tới S1 (Location: Chợ Đà Lạt, Radius: 15km)...")
response = client.post(
    "/api/s1/predict",
    json={
        "location_name": "Chợ Đà Lạt",
        "radius_km": 15
    }
)

print(f"\nStatus Code: {response.status_code}")
print("Response Body:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
