# 🔒 Private Staging Deployment Guide

## Goal
Set up primehaul.co.uk on a real server, but keep it **private for testing only** until you're ready to launch publicly.

---

## 🎯 Strategy

We'll use a **staging subdomain** to keep it private:
- **staging.primehaul.co.uk** - Your private test environment (password protected)
- **primehaul.co.uk** - Reserved for public launch (when ready)

This way you can:
- Test with the real domain
- Access from anywhere (not just localhost)
- Show to friends/partners
- Keep it hidden from Google and public

---

## Step 1: Choose a Hosting Provider (5 minutes)

### Option A: Railway.app (EASIEST - Recommended)

**Why Railway**:
- ✅ Automatic deployments
- ✅ Automatic SSL certificates
- ✅ No server management
- ✅ 5-minute setup
- ✅ $5 credit free

**Cost**: ~$5-20/month depending on usage

### Option B: DigitalOcean (More Control)

**Why DigitalOcean**:
- ✅ Full server control
- ✅ UK data centers
- ✅ Predictable pricing
- ✅ Great for scaling

**Cost**: $6/month (1GB RAM) or $12/month (2GB RAM, recommended)

### Option C: Render.com (Good Free Tier)

**Why Render**:
- ✅ Free tier available
- ✅ Automatic SSL
- ✅ Easy setup

**Cost**: Free tier, then $7/month

---

## 🚀 Option A: Deploy on Railway.app (EASIEST)

### Step 1: Create Railway Account

1. Go to: https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub
4. Get $5 free credit

### Step 2: Deploy Your Project

**Option 1: Deploy from GitHub (Recommended)**

```bash
# 1. Create GitHub repo (if not already done)
cd /Users/primehaul/PrimeHaul/primehaul-os
git init
git add .
git commit -m "Initial commit"

# 2. Create GitHub repo at github.com
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/primehaul-os.git
git push -u origin main

# 3. In Railway dashboard:
# - Click "New Project"
# - Select "Deploy from GitHub repo"
# - Choose your primehaul-os repo
# - Railway will auto-detect Python/FastAPI and deploy
```

**Option 2: Deploy from Local (Quick)**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# Or with Homebrew:
brew install railway

# 2. Login
railway login

# 3. Initialize project
cd /Users/primehaul/PrimeHaul/primehaul-os
railway init

# 4. Deploy
railway up
```

### Step 3: Add Environment Variables

In Railway dashboard:
1. Click on your project
2. Go to "Variables" tab
3. Add these variables:

```bash
# Database (Railway provides PostgreSQL)
DATABASE_URL=postgresql://...  # Railway will provide this

# OpenAI
OPENAI_API_KEY=sk-...

# Mapbox
MAPBOX_ACCESS_TOKEN=pk.eyJ...

# App Settings
SECRET_KEY=your-long-random-secret-key-here

# Twilio (optional for SMS)
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+447123456789

# Stripe (optional for billing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Step 4: Add PostgreSQL Database

In Railway:
1. Click "New" → "Database" → "PostgreSQL"
2. Railway automatically creates `DATABASE_URL` variable
3. Your app will use it automatically

### Step 5: Run Database Migrations

In Railway dashboard:
1. Go to your service
2. Click "Settings" → "Deploy"
3. Add custom start command:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Or run migrations manually:
```bash
railway run alembic upgrade head
```

### Step 6: Connect Your Domain (STAGING SUBDOMAIN)

In Railway dashboard:
1. Click your service
2. Go to "Settings" → "Networking" → "Custom Domain"
3. Add domain: `staging.primehaul.co.uk`
4. Railway gives you a CNAME target (like `xyz.railway.app`)

In your domain registrar (Namecheap, GoDaddy, etc.):
1. Go to DNS settings
2. Add CNAME record:
   ```
   Type: CNAME
   Name: staging
   Value: xyz.railway.app (from Railway)
   TTL: 3600
   ```
3. Save
4. Wait 5-60 minutes for DNS to propagate

### Step 7: SSL Certificate (Automatic)

Railway automatically provides SSL for your custom domain.
Once DNS propagates, you'll access via: `https://staging.primehaul.co.uk`

### Step 8: Add Password Protection (IMPORTANT!)

We need to add basic auth to keep the staging site private.

**Create**: `app/staging_auth.py`

```python
import os
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

STAGING_USERNAME = os.getenv("STAGING_USERNAME", "primehaul")
STAGING_PASSWORD = os.getenv("STAGING_PASSWORD", "changeme123")

def verify_staging_auth(credentials: HTTPBasicCredentials) -> bool:
    """Verify basic auth credentials for staging"""
    correct_username = secrets.compare_digest(credentials.username, STAGING_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, STAGING_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True
```

**Update**: `app/main.py` (add at top)

```python
import os
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials

# Import staging auth if enabled
STAGING_MODE = os.getenv("STAGING_MODE", "false").lower() == "true"

if STAGING_MODE:
    from app.staging_auth import security, verify_staging_auth
```

**Update**: Each public route to require auth in staging mode

```python
# Example for landing page
@app.get("/", response_class=HTMLResponse)
async def landing_page(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security) if STAGING_MODE else None
):
    if STAGING_MODE:
        verify_staging_auth(credentials)
    return templates.TemplateResponse("landing_primehaul_uk.html", {"request": request})
```

**Add to Railway environment variables**:
```bash
STAGING_MODE=true
STAGING_USERNAME=primehaul
STAGING_PASSWORD=your-secret-password-123
```

Now when you visit `https://staging.primehaul.co.uk`, you'll be prompted for username/password!

---

## 🚀 Option B: Deploy on DigitalOcean (More Control)

### Step 1: Create DigitalOcean Account

1. Go to: https://digitalocean.com
2. Sign up (get $200 credit for 60 days)
3. Verify email

### Step 2: Create a Droplet (Server)

1. Click "Create" → "Droplets"
2. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($12/month - 2GB RAM recommended)
   - **Datacenter**: London (UK)
   - **Authentication**: SSH keys (or password)
   - **Hostname**: primehaul-staging
3. Click "Create Droplet"
4. Note the IP address (e.g., 178.128.xxx.xxx)

### Step 3: Connect to Your Server

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx git
```

### Step 4: Set Up PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell, create database and user:
CREATE DATABASE primehaul;
CREATE USER primehaul_user WITH PASSWORD 'your-secure-password-here';
GRANT ALL PRIVILEGES ON DATABASE primehaul TO primehaul_user;
\q
```

### Step 5: Deploy Your Application

```bash
# Create directory
mkdir -p /var/www/primehaul
cd /var/www/primehaul

# Option A: Clone from GitHub
git clone https://github.com/YOUR_USERNAME/primehaul-os.git .

# Option B: Upload from your computer (run from your Mac)
# scp -r /Users/primehaul/PrimeHaul/primehaul-os/* root@YOUR_DROPLET_IP:/var/www/primehaul/

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 6: Create Environment File

```bash
cd /var/www/primehaul
nano .env
```

Add:
```bash
# Database
DATABASE_URL=postgresql://primehaul_user:your-secure-password-here@localhost/primehaul

# OpenAI
OPENAI_API_KEY=sk-...

# Mapbox
MAPBOX_ACCESS_TOKEN=pk.eyJ...

# App Settings
SECRET_KEY=your-long-random-secret-key-here

# Staging Mode
STAGING_MODE=true
STAGING_USERNAME=primehaul
STAGING_PASSWORD=your-secret-password-123

# Twilio (optional)
TWILIO_ENABLED=false
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 7: Run Database Migrations

```bash
source .venv/bin/activate
alembic upgrade head
```

### Step 8: Create Systemd Service

```bash
sudo nano /etc/systemd/system/primehaul.service
```

Add:
```ini
[Unit]
Description=primehaul FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/primehaul
Environment="PATH=/var/www/primehaul/.venv/bin"
ExecStart=/var/www/primehaul/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

[Install]
WantedBy=multi-user.target
```

Save and start:
```bash
# Set permissions
chown -R www-data:www-data /var/www/primehaul

# Start service
systemctl daemon-reload
systemctl start primehaul
systemctl enable primehaul

# Check status
systemctl status primehaul
```

### Step 9: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/primehaul-staging
```

Add:
```nginx
server {
    listen 80;
    server_name staging.primehaul.co.uk;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Prevent search engine indexing
    location = /robots.txt {
        add_header Content-Type text/plain;
        return 200 "User-agent: *\nDisallow: /\n";
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/primehaul-staging /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 10: Point Domain to Server

In your domain registrar (Namecheap, GoDaddy, etc.):

1. Go to DNS settings for primehaul.co.uk
2. Add A record:
   ```
   Type: A
   Name: staging
   Value: YOUR_DROPLET_IP
   TTL: 3600
   ```
3. Save
4. Wait 5-60 minutes for DNS to propagate

Test DNS propagation:
```bash
# On your Mac
dig staging.primehaul.co.uk
# Should show your server IP
```

### Step 11: Install SSL Certificate

```bash
# On your server
certbot --nginx -d staging.primehaul.co.uk

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)
```

Certbot automatically:
- Gets SSL certificate from Let's Encrypt
- Updates Nginx config
- Sets up auto-renewal

### Step 12: Test Your Site

Visit: `https://staging.primehaul.co.uk`

You should be prompted for username/password!
- Username: `primehaul`
- Password: (whatever you set in .env)

---

## 🔒 Making It Extra Private (Optional)

### Option 1: IP Whitelist (Your IP Only)

**In Nginx config**, add before `location /`:
```nginx
# Only allow your IP
allow YOUR_HOME_IP;
deny all;
```

Find your IP: https://whatismyipaddress.com

### Option 2: robots.txt (Prevent Search Engines)

Already included in Nginx config above. Tells Google not to index.

### Option 3: Cloudflare Access (Advanced)

Use Cloudflare to add authentication layer with one-time codes.

---

## ✅ Testing Checklist

Once deployed, test:

- [ ] Visit `https://staging.primehaul.co.uk`
- [ ] Prompted for password? ✓
- [ ] Login works? ✓
- [ ] Landing page loads? ✓
- [ ] All links work (/terms, /privacy, /contact)? ✓
- [ ] Signup creates account? ✓
- [ ] Can login to admin? ✓
- [ ] Customer quote flow works? ✓
- [ ] Photos upload? ✓
- [ ] AI analysis works? ✓
- [ ] Mobile responsive? ✓
- [ ] SSL certificate valid? ✓

---

## 🎯 When Ready to Go Public

### Step 1: Remove Password Protection

Update Railway/server environment variables:
```bash
STAGING_MODE=false  # Disable password protection
```

Restart application.

### Step 2: Point Main Domain

Add DNS record for main domain:
```
Type: A (or CNAME)
Name: @ (or leave blank)
Value: YOUR_SERVER_IP (or staging.primehaul.co.uk)
TTL: 3600
```

### Step 3: Update SSL Certificate

**Railway**: Add `primehaul.co.uk` as custom domain

**DigitalOcean**: Run certbot again:
```bash
certbot --nginx -d primehaul.co.uk -d www.primehaul.co.uk
```

### Step 4: Launch! 🚀

Your site is now live at `https://primehaul.co.uk`

---

## 💰 Estimated Costs

### Railway.app
- $5-20/month (usage-based)
- PostgreSQL included
- SSL included
- No server management

### DigitalOcean
- $12/month for 2GB droplet (recommended)
- PostgreSQL included
- SSL free (Let's Encrypt)
- You manage server

### Domain
- Already own: £0

### Email (Google Workspace)
- £4.60/user/month
- Or Zoho Mail: Free

**Total**: $12-25/month to run entire business

---

## 🆘 Troubleshooting

### "Connection refused" error
```bash
# Check if service is running
systemctl status primehaul

# Check logs
journalctl -u primehaul -f
```

### "502 Bad Gateway" error
```bash
# Nginx can't reach app
# Check if app is running on port 8000
netstat -tulpn | grep 8000
```

### DNS not propagating
- Wait 1-24 hours
- Check: https://whatsmydns.net
- Clear your browser cache

### SSL certificate error
```bash
# Check certificate
certbot certificates

# Renew if needed
certbot renew --dry-run
```

### Can't login to database
```bash
# Test PostgreSQL connection
psql -U primehaul_user -d primehaul -h localhost
```

---

## 📞 Quick Commands Reference

### Railway
```bash
railway login                    # Login to Railway
railway up                       # Deploy
railway run alembic upgrade head # Run migrations
railway logs                     # View logs
railway open                     # Open in browser
```

### DigitalOcean
```bash
ssh root@YOUR_IP                        # Connect to server
systemctl restart primehaul             # Restart app
systemctl status primehaul              # Check status
journalctl -u primehaul -f              # View logs
nginx -t                                # Test Nginx config
systemctl reload nginx                  # Reload Nginx
certbot renew                           # Renew SSL
```

---

## 🎉 You're Done!

You now have:
- ✅ Real domain with SSL (staging.primehaul.co.uk)
- ✅ Password protected (private for testing)
- ✅ Accessible from anywhere (not just localhost)
- ✅ Ready to show partners/investors
- ✅ One command to make it public when ready

**Your staging site is live at**: `https://staging.primehaul.co.uk`

Test everything thoroughly before going public! 🚀

---

**Next Steps**:
1. Choose Railway or DigitalOcean
2. Follow steps above
3. Test thoroughly on staging
4. When ready: flip `STAGING_MODE=false` and go live!
