# 🚀 MRDPOL Core - Production Deployment Guide

## Overview

MRDPOL Core is a comprehensive Manufacturing Resource and Digital Planning Operations Logistics platform built with FastAPI (backend) and React (frontend), designed for production-scale deployment using Docker Compose.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   FastAPI       │    │  PostgreSQL     │
│   (Frontend +   │───▶│   (Backend)     │───▶│   (Database)    │
│  Reverse Proxy) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    Port 80/443            Port 8000              Port 5432
```

## 📋 Prerequisites

- **Docker Engine** 20.10+ 
- **Docker Compose** 2.0+
- **Minimum 4GB RAM** and **20GB disk space**
- **Linux/macOS** (Windows with WSL2)

## 🚀 Quick Deployment

### 1. Download and Extract

```bash
# Download the application files
wget https://github.com/yourusername/mrdpol-core/archive/main.zip
unzip main.zip
cd mrdpol-core-main
```

### 2. Configure Environment

```bash
# Copy and edit the environment file
cp .env.prod .env
nano .env  # Edit with your production values
```

**Required Environment Variables:**
```bash
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_super_secret_key_here
CORS_ORIGINS=https://yourdomain.com
```

### 3. Deploy

```bash
# Make deployment script executable and run
chmod +x deploy.sh
./deploy.sh
```

### 4. Access Application

- **Frontend**: http://localhost (or your domain)
- **API Docs**: http://localhost/api/docs
- **Admin Panel**: http://localhost:5050 (PgAdmin)

**Default Login**: `admin@mrdpol.com` / `admin123` ⚠️ **Change immediately!**

## 🔧 Manual Deployment Steps

If you prefer manual deployment:

### 1. Build and Start Services

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user (optional)
docker-compose exec backend python scripts/create_admin.py
```

### 3. Verify Deployment

```bash
# Check logs
docker-compose logs -f

# Test API health
curl http://localhost/health

# Test frontend
curl http://localhost
```

## 📊 Service Details

### 🗄️ Database (PostgreSQL)
- **Image**: postgres:13-alpine
- **Port**: 5432
- **Data**: Persistent volume `postgres_data`
- **Backup**: Daily automated backups

### 🔧 Backend (FastAPI)
- **Runtime**: Python 3.12 + Gunicorn + Uvicorn
- **Port**: 8000 (internal)
- **Workers**: 4 (configurable)
- **Health Check**: `/health` endpoint

### 🌐 Frontend (React + Nginx)
- **Build**: Multi-stage Docker build
- **Features**: 
  - Static file serving
  - API reverse proxy
  - Rate limiting
  - Gzip compression
  - Security headers

### 🔴 Redis (Caching)
- **Image**: redis:7-alpine
- **Port**: 6379
- **Usage**: Session storage, caching

## 🔐 Security Features

### Network Security
- **Custom Docker network** with isolated communication
- **Rate limiting** on API endpoints
- **CORS protection** with domain whitelist

### Application Security
- **JWT authentication** with configurable expiration
- **Role-based access control** (RBAC)
- **Password hashing** with bcrypt
- **Security headers** (HSTS, CSP, etc.)

### Data Security
- **Database connection encryption**
- **Environment variable isolation**
- **Volume-based data persistence**

## 📈 Monitoring & Logging

### Health Checks
```bash
# Check all services
docker-compose ps

# Individual service health
curl http://localhost/health
curl http://localhost:8000/health
```

### Logs
```bash
# View all logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f backend
docker-compose logs -f nginx
docker-compose logs -f db
```

### Metrics
- **Application metrics**: Available at `/metrics` endpoint
- **Docker stats**: `docker stats`
- **Resource usage**: Built-in Docker monitoring

## 🔄 Management Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View service status
docker-compose ps
```

### Database Management
```bash
# Database backup
docker-compose exec db pg_dump -U mrdpol_user mrdpol_core_db > backup.sql

# Database restore
docker-compose exec -T db psql -U mrdpol_user mrdpol_core_db < backup.sql

# Access database shell
docker-compose exec db psql -U mrdpol_user -d mrdpol_core_db
```

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Run any new migrations
docker-compose exec backend alembic upgrade head
```

## 🛠️ Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker daemon
systemctl status docker

# Check resource usage
docker system df
docker system prune  # Clean up if needed
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Verify database is ready
docker-compose exec db pg_isready -U mrdpol_user
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check application logs
docker-compose logs backend | grep ERROR
```

### Debug Mode
```bash
# Enable debug logging
echo "DEBUG=true" >> .env
docker-compose restart backend
```

## 📁 File Structure

```
mrdpol-core/
├── backend/
│   ├── Dockerfile              # Backend production image
│   ├── app/                   # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── scripts/              # Database and admin scripts
├── frontend/
│   ├── Dockerfile            # Frontend production image  
│   ├── nginx.conf           # Nginx configuration
│   ├── src/                # React application
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Main orchestration file
├── .env.prod              # Environment template
├── deploy.sh             # Automated deployment script
└── README.md            # This file
```

## 🔒 Production Checklist

### Before Going Live
- [ ] Change default admin password
- [ ] Update all environment variables in `.env`
- [ ] Configure SSL certificates
- [ ] Set up domain name and DNS
- [ ] Configure email settings
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups
- [ ] Review security settings
- [ ] Load test the application

### SSL/HTTPS Setup
```bash
# Place SSL certificates in ssl/ directory
mkdir -p ssl/
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Update nginx configuration for HTTPS
# (Modify frontend/nginx.conf as needed)
```

### Backup Strategy
```bash
# Automated daily backups (add to crontab)
0 2 * * * /path/to/mrdpol-core/scripts/backup.sh
```

## 🆘 Support

### Documentation
- **API Documentation**: http://localhost/api/docs
- **User Manual**: Available in admin panel
- **Developer Guide**: `docs/developer-guide.md`

### Getting Help
- **GitHub Issues**: Report bugs and feature requests
- **Email Support**: support@mrdpol.com
- **Community**: Join our Discord/Slack

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 Congratulations! Your MRDPOL Core platform is now running in production mode.**

For additional configuration and advanced features, please refer to the comprehensive documentation in the `docs/` directory.
