# Tài liệu Thiết kế Hệ thống

Dựa vào mã nguồn của dự án `MergePro`, dưới đây là các biểu đồ thiết kế kỹ thuật.

## 1. Sơ đồ Kiến trúc Tổng quan (Architecture Diagram)
Hệ thống được thiết kế theo kiến trúc **Microservices** (Dịch vụ siêu nhỏ), giao tiếp thông qua một API Gateway.

```mermaid
graph TD
    Client[React Frontend / Vite] -->|HTTP Requests| Gateway(FastAPI Gateway - Port 8000)
    
    subgraph Microservices Backend
        Gateway -->|/api/s1| S1[S1: AI Predict Port 8001]
        Gateway -->|/api/v1/places| S2[S2: Booking & Places Port 8002]
        Gateway -->|/auth| S3[S3: Authentication Port 8003]
        Gateway -->|/content| S4[S4: Reviews & Tickets Port 8004]
        Gateway -->|/api/s5| S5[S5: Statistics Port 8005]
        Gateway -->|/api/s6| S6[S6: AI Recommend Port 8006]
    end

    S1 -->|Fetch Data| S5
    S6 -->|Predict Weather| S1
    S6 -->|Recommend Place| S2

    subgraph Databases
        S3 --> DB_App[(app.db)]
        S2 --> DB_S2[(s2_booking.db)]
        S4 --> DB_S4[(s4_content.db)]
        S5 --> DB_S5[(cloud_hunting.db)]
    end
```

## 2. Thiết kế Cơ sở dữ liệu (ERD - Entity Relationship Diagram)
Cấu trúc các bảng dữ liệu chính.

```mermaid
erDiagram
    %% Auth Database (app.db)
    USERS {
        int id PK
        string username
        string email
        string hashed_password
        string display_name
        string role "admin/moderator/user"
        boolean is_active
        datetime created_at
    }

    %% Content Database (s4_content.db)
    REVIEWS {
        int id PK
        int location_id
        string location_name
        int user_id FK
        string username
        string display_name
        int rating
        string comment
        int helpful_count
        boolean is_approved
        datetime created_at
    }

    TICKETS {
        int id PK
        int user_id FK
        string title
        string description
        string status "open/in_progress/closed"
        string category
        datetime created_at
    }

    TICKET_MESSAGES {
        int id PK
        int ticket_id FK
        int sender_id
        string message
        datetime created_at
    }

    %% Booking Database (s2_booking.db)
    PLACES {
        string id PK
        string name
        string category
        float lat
        float lon
        string address
        string province
        string photos_json
        string amenities_json
        boolean is_active
    }

    USERS ||--o{ REVIEWS : "writes"
    USERS ||--o{ TICKETS : "creates"
    TICKETS ||--o{ TICKET_MESSAGES : "contains"
```

## 3. Sơ đồ luồng (Sequence Diagram) - Ví dụ: Luồng Đăng nhập
```mermaid
sequenceDiagram
    actor User
    participant Frontend as React App
    participant Gateway as API Gateway (8000)
    participant Auth as S3 Auth (8003)
    participant DB as app.db

    User->>Frontend: Nhập Username/Password & Bấm Đăng nhập
    Frontend->>Gateway: POST /auth/login
    Gateway->>Auth: Forward request to 8003
    Auth->>DB: Truy vấn User theo Username
    DB-->>Auth: Trả về Hashed Password & Role
    Auth->>Auth: Verify Password (bcrypt)
    Auth->>Auth: Tạo JWT Token (chứa user_id, role)
    Auth-->>Gateway: Trả về Access Token
    Gateway-->>Frontend: Trả về Access Token
    Frontend->>Frontend: Lưu Token vào localStorage & Decode Role
    Frontend-->>User: Chuyển hướng vào App (hoặc Admin Dashboard)
```
