# Sử dụng bản Python 3.13 slim (vừa nhẹ vừa có sẵn bash)
FROM python:3.13-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt bash và công cụ dos2unix (để tự động diệt lỗi CRLF của Windows)
RUN apt-get update && apt-get install -y bash dos2unix && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Ép file script chuyển sang định dạng LF và cấp quyền thực thi
RUN dos2unix render_start.sh
RUN chmod +x render_start.sh

# Lệnh cuối cùng: Khởi chạy dự án bằng bash
CMD ["/bin/bash", "render_start.sh"]
