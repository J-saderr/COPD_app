# Cách Fix Lỗi "Failed to fetch" từ Frontend

## Nguyên nhân

Lỗi "Failed to fetch" xảy ra khi frontend không thể kết nối với backend API. Có thể do:

1. **Backend server chưa chạy hoặc đã crash**
2. **CORS configuration chưa đúng**
3. **API endpoint không đúng**
4. **Network issue**

## Kiểm tra

### 1. Kiểm tra Backend có chạy không

```bash
# Kiểm tra health endpoint
curl http://localhost:8000/healthz

# Nếu không phản hồi, backend chưa chạy
```

### 2. Kiểm tra API endpoint

```bash
# Test API endpoint
curl "http://localhost:8000/api/audio?limit=10"

# Nếu lỗi, kiểm tra log backend
```

### 3. Kiểm tra CORS

Backend đã có CORS config, nhưng cần đảm bảo `.env` có:

```bash
ALLOW_ORIGINS=["http://localhost:3000"]
```

## Giải pháp

### Cách 1: Restart Backend Server

```bash
# Dừng server hiện tại (Ctrl+C)
# Sau đó chạy lại:
cd /Users/vothao/COPD_app/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Cách 2: Kiểm tra và Fix CORS

Đảm bảo file `.env` trong `backend/` có:

```bash
ALLOW_ORIGINS=["http://localhost:3000"]
```

Nếu không có, thêm vào hoặc restart server để reload config.

### Cách 3: Kiểm tra Frontend API URL

Đảm bảo frontend đang dùng đúng URL. Trong `frontend/src/app/page.tsx`:

```typescript
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
```

Có thể tạo file `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Sau đó restart frontend dev server.

### Cách 4: Kiểm tra MongoDB

```bash
# Kiểm tra MongoDB có chạy không
brew services list | grep mongodb

# Nếu chưa chạy:
brew services start mongodb-community
```

## Debug Steps

1. **Mở Browser Console** (F12) và xem error chi tiết
2. **Kiểm tra Network tab** để xem request có được gửi không
3. **Kiểm tra Backend logs** để xem có error không
4. **Test API trực tiếp** với curl để verify backend hoạt động

## Quick Fix Command

```bash
# 1. Kiểm tra backend
curl http://localhost:8000/healthz

# 2. Nếu không OK, restart backend
cd /Users/vothao/COPD_app/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Trong terminal mới, restart frontend
cd /Users/vothao/COPD_app/frontend
npm run dev
```

## Common Issues

### Issue 1: Backend đang chạy nhưng API không phản hồi

**Giải pháp**: Kiểm tra xem có lỗi trong backend log không. Model loading có thể fail.

### Issue 2: CORS error trong browser console

**Giải pháp**: 
- Đảm bảo `ALLOW_ORIGINS` trong `.env` có `http://localhost:3000`
- Restart backend server

### Issue 3: "Connection refused"

**Giải pháp**: Backend chưa chạy hoặc đã crash. Restart backend.

### Issue 4: Model loading error

**Giải pháp**: 
- Kiểm tra model path trong `.env`
- Chạy `python3 scripts/test_model_loading.py` để test model


