#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  CloudHunting - Render.com Start Script
#  Khoi dong tat ca 6 microservices trong 1 process group
# ═══════════════════════════════════════════════════════════

echo "🚀 Dang khoi dong he thong CloudHunting..."

# Khoi dong cac service noi bo (chay ngam)
uvicorn src.s3_auth.main:app --host 0.0.0.0 --port 8003 &
echo "  ✓ S3 Auth (port 8003)"

uvicorn src.s5_statistics.main:app --host 0.0.0.0 --port 8005 &
echo "  ✓ S5 Statistics (port 8005)"

sleep 2  # Cho S3 va S5 san sang truoc

uvicorn src.s1_metrics.main:app --host 0.0.0.0 --port 8001 &
echo "  ✓ S1 Metrics (port 8001)"

uvicorn src.s2_booking.main:app --host 0.0.0.0 --port 8002 &
echo "  ✓ S2 Booking (port 8002)"

uvicorn src.s6_recommend.main:app --host 0.0.0.0 --port 8006 &
echo "  ✓ S6 Recommend (port 8006)"

sleep 2  # Cho cac service san sang

# Khoi dong Gateway (bind vao $PORT cua Render)
# Render chi expose 1 port duy nhat qua bien $PORT
GATEWAY_PORT=${PORT:-8000}
echo "  ✓ Gateway (port $GATEWAY_PORT) - Day la port chinh"
echo "═══════════════════════════════════════════════════════"
echo "  He thong da san sang!"
echo "═══════════════════════════════════════════════════════"

uvicorn src.gateway.main:app --host 0.0.0.0 --port $GATEWAY_PORT
