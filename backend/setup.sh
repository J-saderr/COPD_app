#!/bin/bash
# Setup script for COPD Backend with PyTorch Model

set -e  # Exit on error

echo "=========================================="
echo "COPD Backend Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/7]${NC} Checking Python version..."
python3 --version || { echo -e "${RED}ERROR: Python 3 not found${NC}"; exit 1; }
echo -e "${GREEN}✓ Python version OK${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}ERROR: requirements.txt not found. Please run this script from backend/ directory${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
echo -e "${YELLOW}[2/7]${NC} Checking .env file..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
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

# CORS Configuration
ALLOW_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Please review and update .env file if needed${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Create virtual environment if it doesn't exist
echo -e "${YELLOW}[3/7]${NC} Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi
echo ""

# Activate virtual environment and install dependencies
echo -e "${YELLOW}[4/7]${NC} Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check model file exists
echo -e "${YELLOW}[5/7]${NC} Checking model file..."
MODEL_PATH="/Users/vothao/ICBHI_2017/scripts/best.pth"
if [ -f "$MODEL_PATH" ]; then
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo -e "${GREEN}✓ Model file found: $MODEL_PATH (Size: $SIZE)${NC}"
else
    echo -e "${RED}WARNING: Model file not found at $MODEL_PATH${NC}"
    echo -e "${YELLOW}Please update MODEL_PATH in .env file${NC}"
fi
echo ""

# Check ICBHI directory exists
echo -e "${YELLOW}[6/7]${NC} Checking ICBHI_2017 directory..."
ICBHI_PATH="/Users/vothao/ICBHI_2017"
if [ -d "$ICBHI_PATH" ]; then
    if [ -d "$ICBHI_PATH/model" ] && [ -d "$ICBHI_PATH/BEATs" ]; then
        echo -e "${GREEN}✓ ICBHI_2017 directory found with model architecture${NC}"
    else
        echo -e "${RED}WARNING: ICBHI_2017 directory found but missing model/BEATs subdirectories${NC}"
    fi
else
    echo -e "${RED}WARNING: ICBHI_2017 directory not found at $ICBHI_PATH${NC}"
    echo -e "${YELLOW}Please update ICBHI_PATH in .env file${NC}"
fi
echo ""

# Test model loading
echo -e "${YELLOW}[7/7]${NC} Testing model loading..."
if python3 scripts/test_model_loading.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Model loading test PASSED${NC}"
else
    echo -e "${RED}WARNING: Model loading test FAILED${NC}"
    echo -e "${YELLOW}You can still run the server, but model may not work correctly${NC}"
    echo "Run 'python3 scripts/test_model_loading.py' for details"
fi
echo ""

# Create upload directory
echo "Creating upload directory..."
mkdir -p /tmp/copd/uploads
echo -e "${GREEN}✓ Upload directory created${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review .env file and update if needed"
echo "2. Make sure MongoDB is running:"
echo "   brew services start mongodb-community"
echo "   (or: mongod --config /usr/local/etc/mongod.conf)"
echo ""
echo "3. Activate virtual environment and run server:"
echo "   source .venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Open http://localhost:8000/docs in your browser"
echo ""


