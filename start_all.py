"""
Script khoi dong toan bo he thong CloudHunting.
Chi can chay: python start_all.py
"""
import subprocess
import sys
import time
import os

# Thu muc goc cua du an
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")

# Neu khong co venv thi dung python mac dinh
if not os.path.exists(PYTHON):
    PYTHON = sys.executable

# Danh sach cac service can khoi dong (theo thu tu uu tien)
SERVICES = [
    {"name": "S3 Auth",       "module": "src.s3_auth.main:app",       "port": 8003},
    {"name": "S5 Statistics",  "module": "src.s5_statistics.main:app",  "port": 8005},
    {"name": "S1 Metrics",     "module": "src.s1_metrics.main:app",     "port": 8001},
    {"name": "S2 Booking",     "module": "src.s2_booking.main:app",     "port": 8002},
    {"name": "S6 Recommend",   "module": "src.s6_recommend.main:app",   "port": 8006},
    {"name": "API Gateway",    "module": "src.gateway.main:app",        "port": 8000},
]

def main():
    print("=" * 55)
    print("   CloudHunting - Khoi dong toan bo he thong")
    print("=" * 55)
    
    processes = []
    
    for svc in SERVICES:
        print(f"  Dang khoi dong {svc['name']} (port {svc['port']})...")
        
        # Chay truc tiep bang subprocess (khong dung cmd /k de tranh loi duong dan)
        proc = subprocess.Popen(
            [PYTHON, "-m", "uvicorn", svc["module"],
             "--host", "127.0.0.1", "--port", str(svc["port"]), "--reload"],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        processes.append(proc)
        
        # Cho 2 giay giua moi service de tranh xung dot
        time.sleep(2)
    
    print("-" * 55)
    print(f"  Da khoi dong {len(SERVICES)} services!")
    print()
    print("  Truy cap he thong:")
    print("  -> Web App:     http://127.0.0.1:8000")
    print("  -> Swagger UI:  http://127.0.0.1:8000/docs")
    print("  -> Health:      http://127.0.0.1:8000/health")
    print()
    print("  Cac service rieng le:")
    for svc in SERVICES:
        if svc["name"] != "API Gateway":
            print(f"  -> {svc['name']:<18} http://127.0.0.1:{svc['port']}/docs")
    print("=" * 55)
    print("  Nhan Ctrl+C de tat toan bo he thong.")
    print("=" * 55)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Dang tat he thong...")
        for proc in processes:
            try:
                proc.terminate()
            except Exception:
                pass
        print("  Da tat toan bo services.")

if __name__ == "__main__":
    main()
