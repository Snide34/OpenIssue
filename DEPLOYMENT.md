# OpenIssue Deployment Guide

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- GitHub OAuth App created ([instructions](https://github.com/settings/developers))
- (Optional) Gemini API key for AI features

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/openissue.git
cd openissue

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Start Services

```bash
# Start everything
docker-compose up -d

# Check logs
docker-compose logs -f

# Check health
curl http://localhost:8001/health
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### 4. Stop Services

```bash
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Manual Deployment (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Start backend
python run.py
```

### Frontend Setup

```bash
cd frontend

# Serve with Python
python -m http.server 3000

# Or use any static file server
# npx serve -p 3000
```

### CLI Tool Setup

```bash
cd cli

# Install CLI globally
pip install -e .

# Verify installation
openissue --help

# Scan a directory
openissue scan .
```

---

## Production Deployment

### Environment Variables

```bash
# Required
GITHUB_CLIENT_ID=your_production_client_id
GITHUB_CLIENT_SECRET=your_production_client_secret
GITHUB_REDIRECT_URI=https://yourdomain.com/auth/callback
FRONTEND_URL=https://yourdomain.com
SECRET_KEY=generate-strong-random-key-here

# Optional
GEMINI_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_token_for_higher_rate_limits
```

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use HTTPS for production
- [ ] Set up proper CORS policies
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Backup data directory

### Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Backup

```bash
# Backup data directory
tar -czf openissue-backup-$(date +%Y%m%d).tar.gz backend/data/

# Restore
tar -xzf openissue-backup-20260414.tar.gz
```

---

## Troubleshooting

### Backend won't start

```bash
# Check Python version (3.9+ required)
python --version

# Check dependencies
pip list

# Check logs
docker-compose logs backend
```

### OAuth not working

1. Verify GitHub OAuth app settings:
   - Homepage URL: `http://localhost:3000`
   - Callback URL: `http://localhost:8001/auth/callback`

2. Check environment variables:
   ```bash
   echo $GITHUB_CLIENT_ID
   echo $GITHUB_REDIRECT_URI
   ```

3. Check backend logs for OAuth errors

### Port conflicts

```bash
# Check what's using ports
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# Change ports in docker-compose.yml or .env
```

### CLI not working on Windows

The CLI has been updated to handle Windows encoding. If you still have issues:

```bash
# Set UTF-8 encoding
chcp 65001

# Or use PowerShell instead of CMD
```

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8001/health

# Expected response:
# {"status":"ok","issue_count":40,"metadata":{...}}
```

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Manual deployment
# Check terminal where services are running
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of config
```

### Load Balancer

Use Nginx or HAProxy to distribute traffic across multiple backend instances.

---

## Support

- **Issues**: https://github.com/yourusername/openissue/issues
- **Docs**: https://github.com/yourusername/openissue/wiki
- **Discord**: [Your Discord Link]

---

## License

MIT License - see LICENSE file for details
