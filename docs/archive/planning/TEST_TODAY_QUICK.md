# ⚡ TEST YOUR AI SURVEY IN 30 MINUTES
**Goal:** Get the survey working on localhost so you can test it NOW!

---

## ✅ WHAT YOU HAVE (Good news!)
- ✅ Python environment working
- ✅ Mapbox token configured
- ✅ OpenAI API key in .env (need to verify it's real)

## ❌ WHAT YOU NEED
- ❌ PostgreSQL database (we'll install it now!)

---

## 🚀 30-MINUTE SETUP (Follow These Steps!)

### **STEP 1: Install PostgreSQL (10 minutes)**

**Copy and paste this into Terminal:**

```bash
# Install PostgreSQL (Mac)
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Should see: "Successfully started postgresql@14"
```

**If you don't have Homebrew:**
```bash
# Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install PostgreSQL
brew install postgresql@14
brew services start postgresql@14
```

---

### **STEP 2: Create Database (2 minutes)**

```bash
# Create database
createdb primehaul_local

# Test it works
psql primehaul_local -c "SELECT version();"

# Should show PostgreSQL version info
```

---

### **STEP 3: Update .env File (3 minutes)**

**Open .env file:**
```bash
code .env
# or
nano .env
```

**Add/Update these lines:**
```bash
# Database (ADD THIS)
DATABASE_URL=postgresql://$(whoami)@localhost/primehaul_local

# Check OpenAI key is real (should start with sk-proj- or sk-)
OPENAI_API_KEY=sk-proj-YOUR-REAL-KEY-HERE
# If it says "your-openai-api-key-here" → Get real key from platform.openai.com

# SMTP (optional for testing - can skip for now)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=
# SMTP_PASSWORD=
```

**Save and close (.env)**

---

### **STEP 4: Run Database Migrations (3 minutes)**

```bash
# Make sure you're in project directory
cd /Users/primehaul/PrimeHaul/primehaul-os

# Activate virtual environment
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Should see:
# INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_add_marketplace
```

**If you get errors:** Text me the error message!

---

### **STEP 5: Create Test Company (2 minutes)**

**Run this Python script:**

```bash
python -c "
from app.database import get_db
from app.models import Company, PricingConfig, User
from app.auth import hash_password

db = next(get_db())

# Create test company
company = Company(
    company_name='Test Removals',
    slug='test',
    email='test@primehaul.co.uk',
    subscription_status='active',
    is_active=True,
    primary_color='#2ee59d',
    secondary_color='#000000'
)
db.add(company)
db.commit()
db.refresh(company)

# Create pricing config
pricing = PricingConfig(
    company_id=company.id,
    price_per_cbm=35.00,
    callout_fee=250.00
)
db.add(pricing)

# Create admin user
user = User(
    company_id=company.id,
    email='admin@test.com',
    password_hash=hash_password('test123'),
    full_name='Test User',
    role='owner',
    is_active=True
)
db.add(user)
db.commit()

print('✅ Test company created!')
print('URL: http://localhost:8000/s/test/START')
print('Login: admin@test.com / test123')
"
```

---

### **STEP 6: Start the Server (1 minute)**

```bash
# Start server
uvicorn app.main:app --reload

# Should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Leave this running!** Don't close the terminal.

---

### **STEP 7: TEST THE SURVEY! 🎉 (5 minutes)**

**Open your browser and go to:**

```
http://localhost:8000/s/test/testjob123
```

**You should see:**
1. ✅ Map selection page (pick pickup/dropoff)
2. ✅ Property type selection
3. ✅ Room selection
4. ✅ Photo upload page (TAKE REAL PHOTOS!)
5. ✅ AI analyzes photos 🤖
6. ✅ Shows inventory list
7. ✅ Quote estimate
8. ✅ Customer contact form

**TRY IT NOW!** Take photos of your bedroom/living room with your phone!

---

## 🎯 WHAT TO TEST

### **Test 1: Map Selection**
- [ ] Enter pickup address (your house)
- [ ] Enter dropoff address (friend's house)
- [ ] Map shows locations correctly
- [ ] Click "Continue"

### **Test 2: Property Type**
- [ ] Select "2-Bedroom Flat"
- [ ] Click "Continue"

### **Test 3: Room Selection**
- [ ] Select "Living Room", "Kitchen", "Bedroom 1"
- [ ] Click "Start Scanning"

### **Test 4: Photo Upload (THE IMPORTANT ONE!)**
- [ ] Take 3-5 photos of your living room
- [ ] Upload them
- [ ] Wait for AI to analyze (should take 10-20 seconds)
- [ ] AI should detect: "Sofa, TV, Coffee Table, etc."
- [ ] Click "Next Room"
- [ ] Do same for Kitchen and Bedroom

### **Test 5: Quote Preview**
- [ ] Should show list of all detected items
- [ ] Should show total CBM calculated
- [ ] Should show price estimate (e.g., "£650-£850")
- [ ] Everything look correct?

### **Test 6: Customer Contact**
- [ ] Enter your name, email, phone
- [ ] Click "Submit"
- [ ] Should see success page!

---

## ✅ SUCCESS CHECKLIST

After testing, you should have:
- [ ] PostgreSQL running
- [ ] Database created with tables
- [ ] Server running without errors
- [ ] Successfully completed a survey
- [ ] AI analyzed your photos
- [ ] Got a quote estimate
- [ ] NO errors in terminal

---

## 🐛 TROUBLESHOOTING

### **Error: "PostgreSQL connection refused"**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# If not running:
brew services start postgresql@14
```

### **Error: "OpenAI API error" or "Invalid API key"**
```bash
# Your OpenAI key is wrong/placeholder
# Get real key from: https://platform.openai.com/api-keys
# Update .env with real key
# Restart server (CTRL+C then run uvicorn again)
```

### **Error: "alembic: command not found"**
```bash
# Virtual environment not activated
source .venv/bin/activate

# Try again
alembic upgrade head
```

### **Error: Photos won't upload**
```bash
# Check uploads directory exists
ls -la app/static/uploads/

# If missing:
mkdir -p app/static/uploads/test/testjob123

# Try again
```

### **Browser shows "404 Not Found"**
```bash
# Wrong URL - make sure you use:
http://localhost:8000/s/test/testjob123
# NOT http://localhost:8000/marketplace (that needs different setup)
```

---

## 📱 TEST ON YOUR PHONE TOO!

**Once working on laptop:**

1. Find your local IP address:
```bash
ipconfig getifaddr en0
# Outputs something like: 192.168.1.123
```

2. Open on your phone browser:
```
http://192.168.1.123:8000/s/test/testjob123
```

3. Test the FULL mobile experience (take photos with phone camera!)

---

## 🎉 WHAT TO DO AFTER SUCCESSFUL TEST

**Once it works:**
1. ✅ Screenshot the quote estimate (show Emma!)
2. ✅ Get Emma to test it (send her the URL)
3. ✅ Get 3-5 friends to test it
4. ✅ Collect feedback (what was confusing?)
5. ✅ Fix any bugs you found
6. ✅ You're ready for REAL launch! 🚀

---

## ⏰ TIMELINE

- **0-10 min:** Install PostgreSQL
- **10-15 min:** Create database, update .env
- **15-20 min:** Run migrations, create test company
- **20-22 min:** Start server
- **22-30 min:** Test full survey!

**Total: 30 minutes to working survey!** ✅

---

## 💬 STUCK?

**Text me with:**
1. What step you're on
2. The exact error message
3. Screenshot if possible

**I'll help you get unstuck in minutes!**

---

**NOW GO TEST IT! This is the moment you've been building towards! 🚀**

**Take photos of your room, watch the AI count everything, see the magic happen!**

**YOU'VE GOT THIS! 💪**

---

Created: December 30, 2025
Quick test guide to get you up and running ASAP!
