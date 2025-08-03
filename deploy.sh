#!/bin/bash

# MRDPOL Core Production Deployment Script
# This script deploys the application on a new server

set -e

echo "🚀 MRDPOL Core Production Deployment"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Copying from .env.prod template..."
    cp .env.prod .env
    print_warning "Please edit .env file with your production values before proceeding."
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p ./ssl
mkdir -p ./backups
mkdir -p ./logs

# Set proper permissions
sudo chown -R $USER:$USER ./ssl ./backups ./logs
chmod 755 ./ssl ./backups ./logs

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

print_status "Waiting for services to be healthy..."
sleep 30

# Check if database is ready
print_status "Checking database connection..."
timeout 60s bash -c 'until docker-compose exec -T db pg_isready -U $POSTGRES_USER -d $POSTGRES_DB; do sleep 2; done'

print_status "Running database migrations..."
docker-compose exec backend alembic upgrade head

print_status "Creating default admin user..."
docker-compose exec backend python -c "
from app.db.session import SessionLocal
from app.services.user_service import UserService
from app.schemas.user import UserCreate

db = SessionLocal()
user_service = UserService(db)

# Check if admin user exists
admin_email = 'admin@mrdpol.com'
existing_admin = user_service.get_user_by_email(admin_email)

if not existing_admin:
    admin_user = UserCreate(
        email=admin_email,
        password='admin123',  # Change this!
        full_name='System Administrator',
        is_active=True
    )
    user_service.create_user(admin_user, role='admin')
    print('Default admin user created: admin@mrdpol.com / admin123')
    print('IMPORTANT: Change the default password immediately!')
else:
    print('Admin user already exists')

db.close()
"

# Check service health
print_status "Checking service health..."
for service in db redis backend nginx; do
    if docker-compose ps $service | grep -q "Up (healthy)"; then
        print_status "$service is healthy"
    else
        print_warning "$service is not healthy, checking logs..."
        docker-compose logs --tail=20 $service
    fi
done

# Display application URLs
print_status "Deployment completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost"
echo "   API Documentation: http://localhost/api/docs"
echo "   Health Check: http://localhost/health"
echo "   PgAdmin (if enabled): http://localhost:5050"
echo ""
echo "📋 Default Credentials:"
echo "   Admin User: admin@mrdpol.com"
echo "   Admin Password: admin123 (CHANGE THIS!)"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose logs -f [service]"
echo "   Restart service: docker-compose restart [service]"
echo "   Stop application: docker-compose down"
echo "   Update application: ./deploy.sh"
echo ""
print_warning "Don't forget to:"
print_warning "1. Change default admin password"
print_warning "2. Configure SSL certificates in ./ssl/ directory"
print_warning "3. Set up regular backups"
print_warning "4. Configure monitoring and alerting"
echo ""
print_status "🎉 MRDPOL Core is now running in production mode!"
