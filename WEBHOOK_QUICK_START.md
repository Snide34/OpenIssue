# Webhook Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start the Servers (if not already running)

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 8080
```

### Step 2: Open Webhook Settings

Navigate to:
```
http://localhost:8080/frontend/pages/webhook-settings.html
```

### Step 3: Register a Webhook

1. Enter your repository: `owner/repository`
   - Example: `facebook/react`
   - Example: `openissue/core`

2. Select events:
   - ✅ Issues (recommended)
   - ✅ Pull Requests (optional)
   - ✅ Push (optional)

3. Click **Register Webhook**

4. You'll see a success message

### Step 4: Test It

1. Go to your GitHub repository
2. Create a new issue
3. Return to OpenIssue webhook settings
4. Check "Recent Events" section
5. You should see your event within 10 seconds

### Step 5: Verify

The issue on GitHub should now have:
- ✅ Labels added (type, priority, security)
- ✅ Analysis comment posted
- ✅ Event logged in "Recent Events"

---

## 📋 What Happens Automatically

When you create an issue on GitHub:

```
GitHub Issue Created
        ↓
OpenIssue Receives Webhook
        ↓
Validates Signature
        ↓
Analyzes Issue
        ├─→ Classifies type (bug, feature, etc.)
        ├─→ Scores priority (1-10)
        ├─→ Detects duplicates
        └─→ Scans for vulnerabilities
        ↓
Applies Auto-Actions
        ├─→ Adds labels
        ├─→ Posts comment
        └─→ Creates notification
        ↓
Issue Updated on GitHub
```

---

## 🔧 Configuration

### Environment Variables

Add to `backend/.env`:

```env
# GitHub Webhooks
GITHUB_WEBHOOK_SECRET=your-secret-here
WEBHOOK_URL=http://localhost:8001/webhooks/github
```

### Generate Secret

```bash
openssl rand -hex 32
```

---

## 📊 Monitor Events

### View Recent Events
- Check "Recent Events" section on webhook settings page
- Shows last 10 events
- Displays status (processed, failed, pending)

### View Active Webhooks
- Check "Active Webhooks" section
- Shows registered webhooks
- Shows event count
- Shows last event time

### Refresh Data
- Click "Refresh" button to reload
- Updates in real-time

---

## 🐛 Troubleshooting

### Webhook Not Registering

**Check:**
1. Repository format: `owner/repository` ✓
2. GitHub token permissions ✓
3. Backend is running ✓
4. Network connection ✓

**Fix:**
```bash
# Restart backend
cd backend
python run.py
```

### Events Not Appearing

**Check:**
1. Create a new issue on GitHub
2. Wait 10 seconds
3. Refresh webhook settings page
4. Check "Recent Events" section

**Fix:**
1. Verify webhook is active in GitHub settings
2. Check backend logs for errors
3. Verify GitHub token has write permissions

### Labels Not Applied

**Check:**
1. GitHub token has write permissions
2. Repository is properly connected
3. Analysis services are running

**Fix:**
1. Verify GitHub token
2. Check backend logs
3. Restart backend service

---

## 📚 API Endpoints

### Webhook Endpoints

**Receive Events:**
```
POST /webhooks/github
```

**Get Recent Events:**
```
GET /webhooks/events?limit=10
```

**Health Check:**
```
GET /webhooks/health
```

### Management Endpoints

**Register Webhook:**
```
POST /api/webhooks/register/{owner/repo}?events=issues
```

**List Webhooks:**
```
GET /api/webhooks/list/{owner/repo}
```

**Delete Webhook:**
```
DELETE /api/webhooks/delete/{owner/repo}/{hook_id}
```

---

## 🎯 Common Tasks

### Register Multiple Repositories

1. Go to webhook settings
2. Enter first repository
3. Click "Register Webhook"
4. Repeat for each repository

### Delete a Webhook

1. Find webhook in "Active Webhooks"
2. Click "Delete" button
3. Confirm deletion

### Monitor Specific Events

1. Register webhook
2. Select only desired events
3. Click "Register Webhook"
4. Only selected events will be processed

### Test Webhook

1. Create issue on GitHub
2. Check "Recent Events" in OpenIssue
3. Verify event appears within 10 seconds
4. Check GitHub issue for labels and comments

---

## 🔐 Security

### Webhook Signature Validation
- All webhooks are validated with HMAC-SHA256
- Invalid signatures are rejected
- Prevents unauthorized events

### Authentication
- All API calls require authentication
- Bearer token in Authorization header
- Tokens are encrypted server-side

### Data Privacy
- Only authorized repositories accessed
- Issue content not permanently stored
- Complies with GitHub policies

---

## ⚡ Performance

### Expected Times
- Webhook response: < 200ms
- Analysis: 2-5 seconds
- Label application: < 1 second
- Comment posting: < 2 seconds
- **Total: 5-10 seconds**

### Scalability
- Handles 1000+ events/day
- Async processing
- No blocking operations
- Error recovery

---

## 📖 Documentation

### User Guide
```
docs/webhook-user-guide.md
```

### API Documentation
```
docs/api_documentation.md
```

### System Design
```
docs/system_design.md
```

---

## 🆘 Support

### Check These First
1. Webhook settings page loads? ✓
2. Backend is running? ✓
3. Frontend is running? ✓
4. Repository format correct? ✓
5. GitHub token valid? ✓

### Debug Steps
1. Check browser console for errors
2. Check backend logs for errors
3. Verify webhook in GitHub settings
4. Test with curl:
   ```bash
   curl http://localhost:8001/webhooks/health
   ```

### Get Help
1. Read user guide: `docs/webhook-user-guide.md`
2. Check troubleshooting section
3. Review backend logs
4. Contact support with:
   - Repository name
   - Error message
   - Steps to reproduce

---

## ✅ Checklist

### Setup
- [ ] Backend running on port 8001
- [ ] Frontend running on port 8080
- [ ] Webhook settings page loads
- [ ] GitHub token configured
- [ ] Webhook secret configured

### Registration
- [ ] Repository name entered correctly
- [ ] Events selected
- [ ] Webhook registered successfully
- [ ] Success message displayed
- [ ] Webhook appears in active list

### Testing
- [ ] Created test issue on GitHub
- [ ] Event appears in "Recent Events"
- [ ] Labels added to issue
- [ ] Comment posted with analysis
- [ ] Status shows "processed"

### Verification
- [ ] Webhook active in GitHub settings
- [ ] Event processing time < 10 seconds
- [ ] All auto-actions working
- [ ] No errors in logs
- [ ] Ready for production

---

## 🎓 Next Steps

### Learn More
1. Read full user guide: `docs/webhook-user-guide.md`
2. Review API documentation: `docs/api_documentation.md`
3. Check system design: `docs/system_design.md`

### Advanced Features
1. Custom automation rules (coming soon)
2. Event replay functionality (coming soon)
3. Webhook analytics (coming soon)
4. Slack integration (coming soon)

### Get Involved
1. Report bugs and issues
2. Suggest features
3. Contribute to development
4. Help with documentation

---

## 📞 Quick Links

- **Webhook Settings:** http://localhost:8080/frontend/pages/webhook-settings.html
- **Dashboard:** http://localhost:8080/frontend/pages/dashboard.html
- **Settings:** http://localhost:8080/frontend/pages/settings.html
- **Backend API:** http://localhost:8001
- **Health Check:** http://localhost:8001/webhooks/health

---

**Ready to go!** 🚀

Start with Step 1 above and you'll have webhooks running in 5 minutes.

