import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

def main():
    print("Đang tải dữ liệu từ historical_weather.csv...")
    try:
        df = pd.read_csv("historical_weather.csv")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file historical_weather.csv. Hãy chạy data_pipeline.py trước.")
        return

    # Các tính năng đầu vào (Features) cho mô hình
    features = [
        'temperature_2m',
        'relative_humidity_2m',
        'wind_speed_10m',
        'cloud_cover_low',
        'cloud_cover_high',
        'pressure_msl',          # Áp suất khí quyển — điều kiện ổn định nghịch nhiệt
        'spread'
    ]
    target = 'is_cloud_hunting_good'

    X = df[features]
    y = df[target]

    print(f"Tổng số mẫu: {len(X)}")
    print(f"Số lượng positive (có mây): {y.sum()}")

    # Chia dữ liệu: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Đang huấn luyện mô hình RandomForestClassifier...")
    # Khởi tạo mô hình: sử dụng class_weight='balanced' vì dữ liệu mây đẹp (positive) khá hiếm
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    
    # Huấn luyện
    model.fit(X_train, y_train)

    print("Đang đánh giá mô hình...")
    y_pred = model.predict(X_test)
    
    print("\n--- KẾT QUẢ ĐÁNH GIÁ (TEST SET) ---")
    print(f"Độ chính xác (Accuracy): {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print("\nBáo cáo chi tiết (Classification Report):")
    print(classification_report(y_test, y_pred))

    # Lưu mô hình
    model_path = "cloud_model.pkl"
    joblib.dump(model, model_path)
    print(f"\n✅ Đã lưu mô hình thành công vào: {model_path}")

if __name__ == "__main__":
    main()
