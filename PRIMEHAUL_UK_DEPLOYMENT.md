# 🚀 primehaul.co.uk Deployment Guide

## 🎯 Overview

You now have a **production-ready** marketing website for primehaul.co.uk that's designed to:
- ✅ Convert removal companies into paying customers
- ✅ Look ultra-professional and trustworthy
- ✅ Not reveal technical implementation details (no copycat risk)
- ✅ Focus on benefits, not features
- ✅ Drive signups with strong CTAs

---

## 📁 What's Been Created

### New Files:
1. **`app/templates/landing_primehaul_uk.html`** - Main marketing landing page
   - Benefit-focused hero section
   - Problem/solution framework
   - Social proof & testimonials
   - Pricing section
   - FAQ
   - Signup form
   - Professional design

2. **`app/templates/terms.html`** - Terms of Service
   - GDPR compliant
   - Clear liability limitations
   - UK law focused

3. **`app/templates/privacy.html`** - Privacy Policy
   - GDPR/UK GDPR compliant
   - Data ownership clarity
   - Security commitments

4. **`app/templates/contact.html`** - Contact page
   - Multiple contact methods
   - Support channels
   - CTA to signup

### Updated Files:
- **`app/main.py`** - Added routes for:
  - `/` - Landing page (new primehaul.co.uk version)
  - `/terms` - Terms of Service
  - `/privacy` - Privacy Policy
  - `/contact` - Contact page

---

## 🌐 Domain Setup (primehaul.co.uk)

### Step 1: DNS Configuration

**Option A: Deploy on Your Own Server**

1. Point your domain to your server's IP:
   ```
   Type: A Record
   Name: @
   Value: YOUR_SERVER_IP
   TTL: 3600
   ```

2. Add www subdomain (optional):
   ```
   Type: CNAME
   Name: www
   Value: primehaul.co.uk
   TTL: 3600
   ```

**Option B: Use a Platform (Recommended for Easy SSL)**

Deploy on:
- **Railway.app** - Easiest, automatic SSL
- **Render.com** - Free tier with SSL
- **Fly.io** - Fast, global CDN
- **DigitalOcean App Platform** - £5/month

---

## 🔒 SSL Certificate (HTTPS)

**Critical**: You MUST have HTTPS for:
- Customer trust
- Google rankings
- Payment processing
- GDPR compliance

### Option A: Automatic SSL (Easiest)
Use Railway, Render, or Fly.io - they handle SSL automatically.

### Option B: Manual SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d primehaul.co.uk -d www.primehaul.co.uk

# Auto-renewal (runs every 12 hours)
sudo systemctl enable certbot.timer
```

---

## 🚀 Deployment Options

### Option 1: Railway.app (Recommended - Easiest)

1. **Create Railway account**: railway.app
2. **Connect GitHub repo** (or create new project)
3. **Deploy**:
   ```bash
   # In your project root
   railway link
   railway up
   ```
4. **Add environment variables** in Railway dashboard
5. **Connect custom domain**: primehaul.co.uk
6. **Done!** SSL is automatic.

**Cost**: ~$5-20/month depending on usage

---

### Option 2: Your Own Server (DigitalOcean, Linode, etc.)

```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx postgresql certbot

# 3. Clone your repo
cd /var/www
git clone YOUR_REPO primehaul-os
cd primehaul-os

# 4. Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Set up environment variables
nano .env
# Add all your env vars (DATABASE_URL, OPENAI_API_KEY, etc.)

# 6. Run database migrations
alembic upgrade head

# 7. Set up systemd service
sudo nano /etc/systemd/system/primehaul.service
```

**primehaul.service**:
```ini
[Unit]
Description=primehaul FastAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/primehaul-os
Environment="PATH=/var/www/primehaul-os/.venv/bin"
ExecStart=/var/www/primehaul-os/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Start service
sudo systemctl start primehaul
sudo systemctl enable primehaul

# 9. Configure Nginx
sudo nano /etc/nginx/sites-available/primehaul
```

**Nginx config**:
```nginx
server {
    listen 80;
    server_name primehaul.co.uk www.primehaul.co.uk;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 10. Enable site
sudo ln -s /etc/nginx/sites-available/primehaul /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 11. Get SSL certificate
sudo certbot --nginx -d primehaul.co.uk -d www.primehaul.co.uk

# 12. Done!
```

---

## 🧪 Testing Your Deployment

Before going live, test these:

1. **Landing page loads**: https://primehaul.co.uk
2. **SSL certificate valid**: Check for padlock icon
3. **All links work**:
   - Terms: https://primehaul.co.uk/terms
   - Privacy: https://primehaul.co.uk/privacy
   - Contact: https://primehaul.co.uk/contact
4. **Signup form works**: https://primehaul.co.uk/#signup
5. **Mobile responsive**: Test on phone
6. **Page load speed**: Use PageSpeed Insights

---

## 📧 Email Setup

Set up email addresses mentioned in contact page:

1. **hello@primehaul.co.uk** - General inquiries
2. **privacy@primehaul.co.uk** - Privacy/GDPR requests
3. **sales@primehaul.co.uk** - Pre-sales questions
4. **support@primehaul.co.uk** - Customer support

**Quick Setup Options**:
- **Google Workspace**: £4.60/user/month, professional
- **Zoho Mail**: Free for 5 users, good enough
- **ProtonMail**: Privacy-focused, £4/month

---

## 🎨 Branding Customizations (Optional)

### Change Colors
Edit `landing_primehaul_uk.html`, line 23:
```css
:root {
  --prime-green: #2ee59d;  /* Change to your brand color */
}
```

### Add Logo Image
Instead of text logo, add an image:
```html
<div class="logo">
  <img src="/static/logo.png" alt="primehaul" style="height: 32px;" />
</div>
```

### Change Stats
Edit testimonials and stats in `landing_primehaul_uk.html` to match your actual numbers.

---

## 📊 Analytics Setup (Recommended)

### Add Google Analytics
Add before `</head>` in `landing_primehaul_uk.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Add Facebook Pixel (Optional)
```html
<!-- Meta Pixel -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');
</script>
```

---

## 🔥 Go-Live Checklist

Before announcing to the world:

- [ ] Domain pointing to server (DNS propagated)
- [ ] SSL certificate installed (https:// works)
- [ ] All pages load correctly
- [ ] Signup form creates accounts
- [ ] Email addresses set up and working
- [ ] Mobile responsive (test on real phone)
- [ ] Page load speed under 3 seconds
- [ ] Google Analytics tracking
- [ ] Terms & Privacy pages complete
- [ ] No test/placeholder content visible
- [ ] All external links work
- [ ] Favicon added
- [ ] Social media preview (Open Graph) working

---

## 🎯 Marketing Strategy

### Day 1: Soft Launch
1. Send to 10 removal company friends
2. Get feedback on copy and flow
3. Fix any issues

### Week 1: Local Launch
1. Post in removal industry Facebook groups
2. Email 100 removal companies in your area
3. Offer special launch pricing

### Month 1: Scale
1. Run Google Ads (target: "removal quote software")
2. SEO: Blog posts about removal industry
3. Partner with removal industry associations

### Email Template (Cold Outreach):
```
Subject: Instant quotes for your removal company?

Hi [Name],

Are you losing customers because you take too long to send quotes?

primehaul generates instant, accurate removal quotes using AI.
Your customers snap photos. AI calculates volume. You approve from your phone.

30-day free trial. No credit card needed.
https://primehaul.co.uk

Takes 5 minutes to set up. Worth a look?

Best,
[Your Name]
```

---

## 💡 What Makes This Landing Page Special

### Copycat Protection:
- ✅ Benefits-focused, not technical
- ✅ No mention of specific AI models
- ✅ No database/architecture details
- ✅ No screenshots of admin panel
- ✅ Vague "AI analyzes photos" language

### Conversion Optimized:
- ✅ Clear headline targeting pain points
- ✅ Social proof (testimonials, stats)
- ✅ Multiple CTAs throughout page
- ✅ Urgency element (limited offer)
- ✅ Low friction signup (no credit card)
- ✅ FAQ addresses objections
- ✅ Professional design builds trust

### SEO Ready:
- ✅ Semantic HTML structure
- ✅ Meta descriptions
- ✅ Open Graph tags
- ✅ Fast loading (minimal JS)
- ✅ Mobile responsive

---

## 🆘 Troubleshooting

**Problem**: Domain doesn't load
- Check DNS propagation: whatsmydns.net
- Wait 24-48 hours for DNS to update

**Problem**: SSL certificate error
- Run: `sudo certbot renew --dry-run`
- Check nginx config: `sudo nginx -t`

**Problem**: Signup form doesn't work
- Check `/auth/signup` route is working
- Check database connection
- Check logs: `sudo journalctl -u primehaul -f`

**Problem**: Page loads slow
- Enable gzip in nginx
- Add caching headers
- Optimize images (if you add any)
- Use CDN for static files

---

## 📞 Need Help?

If you get stuck:
1. Check server logs: `sudo journalctl -u primehaul -f`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Test locally first: `uvicorn app.main:app --reload`

---

## 🎉 You're Ready!

Your primehaul.co.uk website is now:
- ✅ Professional and trustworthy
- ✅ Conversion-optimized
- ✅ Copycat-protected
- ✅ GDPR compliant
- ✅ Mobile responsive
- ✅ Ready to make sales

**Next Steps**:
1. Deploy to your domain
2. Set up email addresses
3. Add Google Analytics
4. Start marketing!

Good luck! You're about to dominate the UK removal quote market. 🚀

---

**Built with**: Love, AI, and a lot of coffee ☕
**Status**: Production Ready
**Last Updated**: January 2026
