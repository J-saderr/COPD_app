# Hướng dẫn Setup và Chạy Website với PyTorch Model

## Bước 1: Cấu hình Environment

Tạo file `.env` trong thư mục `backend/`:

```bash
cd /Users/vothao/COPD_app/backend
cat > .env << 'EOF'
# Model Configuration - PyTorch
MODEL_TYPE=pytorch
MODEL_PATH=/Users/vothao/ICBHI_2017/scripts/best.pth
ICBHI_PATH=/Users/vothao/ICBHI_2017

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/copd_app
MONGO_DB=copd_app

# Storage Configuration
UPLOAD_DIR=/tmp/copd/uploads

# CORS Configuration (for frontend)
ALLOW_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
EOF
```

Hoặc chỉnh sửa file `.env` thủ công với các giá trị trên.

## Bước 2: Cài đặt Dependencies

```bash
cd /Users/vothao/COPD_app/backend

# Tạo virtual environment (nếu chưa có)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

**Lưu ý**: Cài đặt PyTorch có thể mất vài phút, đặc biệt nếu download phiên bản mới.

## Bước 3: Kiểm tra MongoDB

Đảm bảo MongoDB đang chạy:

```bash
# Kiểm tra MongoDB có chạy không
mongosh --eval "db.adminCommand('ping')" || echo "MongoDB chưa chạy"

# Nếu chưa chạy, khởi động MongoDB
# Trên macOS với Homebrew:
brew services start mongodb-community

# Hoặc chạy trực tiếp:
mongod --config /usr/local/etc/mongod.conf
```

## Bước 4: Kiểm tra Model có Load được không

```bash
cd /Users/vothao/COPD_app/backend

# Test model loading
python3 scripts/test_model_loading.py
```

Nếu thành công, bạn sẽ thấy:
```
✅ Model file found: /Users/vothao/ICBHI_2017/scripts/best.pth
✅ Checkpoint loaded successfully!
✅ Model structure validated!
✅ Test PASSED: Model can be loaded!
```

## Bước 5: Tạo thư mục Upload (nếu chưa có)

```bash
mkdir -p /tmp/copd/uploads
```

## Bước 6: Chạy Backend Server

```bash
cd /Users/vothao/COPD_app/backend

# Đảm bảo virtual environment đã được activate
source .venv/bin/activate

# Chạy server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

**Lưu ý**: Lần đầu load PyTorch model có thể mất vài giây. Bạn sẽ thấy log khi model được load.

## Bước 7: Kiểm tra Backend API

Mở terminal mới và test API:

```bash
# Kiểm tra health endpoint
curl http://localhost:8000/docs

# Hoặc test với file audio (nếu có)
curl -X POST "http://localhost:8000/api/audio/" \
  -F "file=@/path/to/your/audio.wav"
```

## Bước 8: Chạy Frontend (nếu có)

```bash
cd /Users/vothao/COPD_app/frontend

# Cài đặt dependencies (lần đầu)
npm install

# Chạy frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

## Bước 9: Truy cập Website

Mở browser và truy cập:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000

## Troubleshooting

### Lỗi: "Cannot load model without ICBHI_2017 architecture"

**Giải pháp**: 
- Kiểm tra `ICBHI_PATH` trong `.env` có đúng không
- Đảm bảo thư mục ICBHI_2017 có đầy đủ files:
  ```bash
  ls -la /Users/vothao/ICBHI_2017/model/
  ls -la /Users/vothao/ICBHI_2017/BEATs/
  ```

### Lỗi: "Checkpoint not found"

**Giải pháp**: 
- Kiểm tra `MODEL_PATH` trong `.env` có đúng không
- Đảm bảo file `best.pth` tồn tại:
  ```bash
  ls -lh /Users/vothao/ICBHI_2017/scripts/best.pth
  ```

### Lỗi: "ModuleNotFoundError: No module named 'torch'"

**Giải pháp**: 
- Đảm bảo đã activate virtual environment
- Cài đặt lại dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Lỗi: MongoDB connection error

**Giải pháp**: 
- Kiểm tra MongoDB có chạy không:
  ```bash
  brew services list | grep mongodb
  ```
- Kiểm tra `MONGO_URI` trong `.env` có đúng không
- Thử kết nối MongoDB trực tiếp:
  ```bash
  mongosh mongodb://localhost:27017/copd_app
  ```

### Model load chậm

**Lưu ý**: PyTorch model lớn (>200MB), lần đầu load có thể mất 10-30 giây. Điều này là bình thường.

## Kiểm tra Model đang dùng

Để kiểm tra model type đang được sử dụng, xem log khi start server:

```
INFO:     Application startup complete.
INFO:     Model type: pytorch
INFO:     Model path: /Users/vothao/ICBHI_2017/scripts/best.pth
```

Hoặc kiểm tra qua API:

```bash
curl http://localhost:8000/docs
# Xem API documentation
```

## Cấu trúc Files

```
backend/
├── .env                    # Configuration file (cần tạo)
├── app/
│   ├── core/
│   │   └── config.py       # Settings (đã cập nhật)
│   ├── models/
│   │   └── hftt_model.py   # Model loader
│   ├── services/
│   │   ├── inference.py    # ONNX inference
│   │   └── pytorch_inference.py  # PyTorch inference
│   └── routers/
│       └── audio.py        # API routes (đã cập nhật)
├── scripts/
│   └── test_model_loading.py  # Test script
└── requirements.txt        # Dependencies (đã cập nhật)
```

## Tóm tắt Quick Start

```bash
# 1. Tạo .env file
cd /Users/vothao/COPD_app/backend
cat > .env << 'EOF'
MODEL_TYPE=pytorch
MODEL_PATH=/Users/vothao/ICBHI_2017/scripts/best.pth
ICBHI_PATH=/Users/vothao/ICBHI_2017
MONGO_URI=mongodb://localhost:27017/copd_app
EOF

# 2. Cài đặt dependencies
source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Test model
python3 scripts/test_model_loading.py

# 4. Chạy server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


