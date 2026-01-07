#!/bin/bash

# PrimeHaul OS - Quick Start Test Script
# Run this to start testing in 1 command!

set -e  # Exit on error

echo "🚀 PrimeHaul OS - Starting Test Environment..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating one...${NC}"
    cat > .env << 'EOF'
DATABASE_URL=sqlite:///./primehaul_test.db
JWT_SECRET_KEY=test-secret-key-for-local-development-only
OPENAI_API_KEY=your-key-here
OPENAI_VISION_MODEL=gpt-4o-mini
MAPBOX_ACCESS_TOKEN=your-token-here
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID=price_xxx
APP_ENV=development
APP_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY and MAPBOX_ACCESS_TOKEN${NC}"
    echo ""
fi

# Check if database exists
if [ ! -f primehaul_test.db ]; then
    echo -e "${BLUE}📊 Creating database tables...${NC}"
    python3 -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database created!')
" || {
        echo -e "${YELLOW}⚠️  Database creation failed. Installing dependencies...${NC}"
        pip install -r requirements.txt
        python3 -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database created!')
"
    }
fi

# Get local IP
echo ""
echo -e "${BLUE}🔍 Finding your local IP address...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    LOCAL_IP=$(hostname -I | awk '{print $1}')
else
    # Windows
    LOCAL_IP=$(ipconfig | grep "IPv4" | head -1 | awk '{print $NF}')
fi

echo -e "${GREEN}✅ Local IP: $LOCAL_IP${NC}"
echo ""

# Display URLs
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 PrimeHaul OS is ready to test!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📱 On your PHONE (same WiFi network):${NC}"
echo -e "   Customer Survey: ${YELLOW}http://$LOCAL_IP:8000/s/your-company/test123${NC}"
echo ""
echo -e "${BLUE}💻 On your PC:${NC}"
echo -e "   Signup:          ${YELLOW}http://localhost:8000/auth/signup${NC}"
echo -e "   Admin Dashboard: ${YELLOW}http://localhost:8000/your-company/admin/dashboard${NC}"
echo -e "   Branding:        ${YELLOW}http://localhost:8000/your-company/admin/branding${NC}"
echo -e "   Pricing:         ${YELLOW}http://localhost:8000/your-company/admin/pricing${NC}"
echo -e "   Analytics:       ${YELLOW}http://localhost:8000/your-company/admin/analytics${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}🚀 Starting server...${NC}"
echo -e "${YELLOW}Press CTRL+C to stop${NC}"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
