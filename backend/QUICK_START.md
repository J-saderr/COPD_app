# Quick Start Guide - Chạy Website với PyTorch Model

## 🚀 Cách nhanh nhất (Tự động)

```bash
cd /Users/vothao/COPD_app/backend
./setup.sh
```

Script sẽ tự động:
- Tạo `.env` file
- Setup virtual environment
- Cài đặt dependencies
- Kiểm tra model file
- Test model loading

Sau đó chạy:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 Cách thủ công (Từng bước)

### Bước 1: Tạo file `.env`

```bash
cd /Users/vothao/COPD_app/backend
cat > .env << 'EOF'
MODEL_TYPE=pytorch
MODEL_PATH=/Users/vothao/ICBHI_2017/scripts/best.pth
ICBHI_PATH=/Users/vothao/ICBHI_2017
MONGO_URI=mongodb://localhost:27017/copd_app
UPLOAD_DIR=/tmp/copd/uploads
EOF
```

### Bước 2: Cài đặt dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Bước 3: Test model

```bash
python3 scripts/test_model_loading.py
```

### Bước 4: Khởi động MongoDB (nếu chưa chạy)

```bash
# Kiểm tra
brew services list | grep mongodb

# Khởi động
brew services start mongodb-community
```

### Bước 5: Chạy backend server

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: **http://localhost:8000**

### Bước 6: Chạy frontend (nếu cần)

```bash
cd /Users/vothao/COPD_app/frontend
npm install  # Chỉ lần đầu
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

## ✅ Kiểm tra

1. **Backend API Docs**: http://localhost:8000/docs
2. **Upload audio**: Sử dụng API endpoint `/api/audio/` hoặc frontend
3. **Check health**: http://localhost:8000

## 🔍 Troubleshooting

### Model không load được?

```bash
# Test model
python3 scripts/test_model_loading.py

# Kiểm tra file
ls -lh /Users/vothao/ICBHI_2017/scripts/best.pth

# Kiểm tra ICBHI_2017
ls -la /Users/vothao/ICBHI_2017/model/
```

### MongoDB không kết nối?

```bash
# Khởi động MongoDB
brew services start mongodb-community

# Test kết nối
mongosh mongodb://localhost:27017/copd_app
```

### Dependencies chưa cài?

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 📚 Tài liệu chi tiết

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Hướng dẫn chi tiết
- [PYTORCH_MODEL_SETUP.md](PYTORCH_MODEL_SETUP.md) - Cấu hình PyTorch model
- [README.md](README.md) - Tổng quan


