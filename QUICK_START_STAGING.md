# 🚀 Quick Start: Private Staging Setup

## TL;DR
Get primehaul.co.uk running on a real server, but keep it password-protected for testing before going public.

**Time needed**: 30 minutes
**Cost**: $5-12/month
**Result**: Private staging site at `https://staging.primehaul.co.uk`

---

## Option 1: Railway.app (EASIEST - Recommended)

### Step 1: Create Railway Account (2 min)
1. Go to: https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway
4. ✅ Get $5 free credit

### Step 2: Create Project (1 min)
1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. If you don't have GitHub repo yet, first:
   ```bash
   cd /Users/primehaul/PrimeHaul/primehaul-os
   git init
   git add .
   git commit -m "Initial commit"
   # Create repo on github.com, then:
   git remote add origin https://github.com/YOUR_USERNAME/primehaul-os.git
   git push -u origin main
   ```
4. Select your primehaul-os repo
5. Railway auto-deploys ✅

### Step 3: Add PostgreSQL Database (1 min)
1. In Railway project, click "New"
2. Choose "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL` ✅
4. Done!

### Step 4: Add Environment Variables (5 min)
Click your service → "Variables" tab → Add these:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here
MAPBOX_ACCESS_TOKEN=pk.your-token-here
SECRET_KEY=your-long-random-key-here

# Staging Mode (IMPORTANT!)
STAGING_MODE=true
STAGING_USERNAME=primehaul
STAGING_PASSWORD=YourSecurePassword123

# Optional - Twilio SMS
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+447123456789
```

**To generate SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Step 5: Configure Start Command (2 min)
1. Click your service → "Settings"
2. Find "Deploy" section
3. Set custom start command:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Save

### Step 6: Connect Domain (5 min)

**In Railway**:
1. Click your service
2. "Settings" → "Networking" → "Custom Domain"
3. Add: `staging.primehaul.co.uk`
4. Railway shows you a CNAME (like `xyz.railway.app`)

**In Your Domain Registrar** (Namecheap, GoDaddy, etc.):
1. Login to your domain dashboard
2. Find DNS settings for `primehaul.co.uk`
3. Add CNAME record:
   - **Type**: CNAME
   - **Name**: staging
   - **Target**: xyz.railway.app (from Railway)
   - **TTL**: 3600
4. Save
5. Wait 5-60 minutes for DNS to update

**Check DNS propagation**:
https://whatsmydns.net/?s=staging.primehaul.co.uk

### Step 7: Test Your Site (2 min)
1. Visit: `https://staging.primehaul.co.uk`
2. You'll see a login popup! 🔒
3. Enter:
   - Username: `primehaul`
   - Password: (whatever you set)
4. You're in! ✅

**Test these pages**:
- Landing: https://staging.primehaul.co.uk/
- Terms: https://staging.primehaul.co.uk/terms
- Privacy: https://staging.primehaul.co.uk/privacy
- Contact: https://staging.primehaul.co.uk/contact
- Signup: https://staging.primehaul.co.uk/auth/signup

---

## Option 2: DigitalOcean (More Control)

### Why DigitalOcean?
- Full server control
- UK data center (faster for UK customers)
- Predictable $12/month cost

### Quick Setup

**Step 1**: Create droplet at digitalocean.com
- Image: Ubuntu 22.04
- Plan: Basic $12/month (2GB RAM)
- Datacenter: London
- Create

**Step 2**: Follow detailed guide in `STAGING_DEPLOYMENT_GUIDE.md`

---

## Testing Your Staging Site

### ✅ Checklist

Try these as if you're a customer:

- [ ] Visit staging.primehaul.co.uk
- [ ] Password prompt appears
- [ ] Login works
- [ ] Landing page looks good
- [ ] All links work
- [ ] Sign up and create account
- [ ] Login to admin dashboard
- [ ] Create a test quote
- [ ] Upload photos
- [ ] AI analysis works
- [ ] Quote appears correctly
- [ ] Mobile version works (test on phone)

### Show Friends/Partners

Share:
- URL: https://staging.primehaul.co.uk
- Username: primehaul
- Password: (your password)

Get feedback before going public!

---

## Going Live (When Ready)

### Step 1: Remove Password Protection

**In Railway**:
1. Go to Variables
2. Change: `STAGING_MODE=false`
3. Save (auto-redeploys)

**Or in DigitalOcean**:
```bash
ssh root@YOUR_IP
cd /var/www/primehaul
nano .env
# Change STAGING_MODE=false
sudo systemctl restart primehaul
```

### Step 2: Point Main Domain

Add another DNS record:
- **Type**: A (or CNAME)
- **Name**: @ (or blank for root)
- **Target**: Your Railway URL or server IP
- **TTL**: 3600

### Step 3: Update SSL

**Railway**: Add `primehaul.co.uk` as custom domain (automatic SSL)

**DigitalOcean**:
```bash
sudo certbot --nginx -d primehaul.co.uk -d www.primehaul.co.uk
```

### Step 4: LAUNCH! 🚀

Your site is now live at `https://primehaul.co.uk` without password!

---

## Costs Summary

### Railway
- **Free**: $5 credit (covers first month)
- **After**: $5-20/month (usage-based)
- **Includes**: Database, SSL, hosting
- **Total first month**: Free

### DigitalOcean
- **Droplet**: $12/month
- **SSL**: Free (Let's Encrypt)
- **Database**: Included
- **Total**: $12/month

### Other
- **Domain**: You already own it
- **Email** (optional): £4.60/month (Google Workspace)

**Total to run everything**: $12-25/month

---

## Common Issues

### "Connection refused" or "502 Bad Gateway"
- Wait 2-3 minutes for Railway to finish deploying
- Check Railway logs for errors

### DNS not working
- Wait up to 24 hours for DNS propagation
- Check https://whatsmydns.net
- Clear browser cache

### Password not working
- Check you set `STAGING_MODE=true` in variables
- Username is case-sensitive
- Try incognito/private browser window

### AI not working
- Check `OPENAI_API_KEY` is set correctly
- Verify OpenAI account has credits
- Check Railway logs for errors

---

## Need More Help?

📖 **Detailed Guide**: See `STAGING_DEPLOYMENT_GUIDE.md` for full instructions

🔧 **Troubleshooting**: Railway logs show all errors
```bash
# Railway CLI (if installed)
railway logs

# Or view in Railway dashboard
```

---

## 🎉 You're Ready!

Once deployed:
1. ✅ Real domain with SSL
2. ✅ Password protected (private)
3. ✅ Test from anywhere
4. ✅ Show to partners
5. ✅ Go public with one click

**Next**: Deploy and start testing! 🚀
