# MRDPOL Core

**MRDPOL Core** is a comprehensive ERP (Enterprise Resource Planning) platform designed for production management and organizational process optimization.

## Features

- **Warehouse Management**: Complete inventory and request tracking
- **Production Planning**: Advanced route cards and workflow management  
- **Quality Control**: Integrated QC processes and approvals
- **Subcontractor Management**: Seamless coordination with external partners
- **Real-time Tracking**: Production progress monitoring and notifications
- **User Management**: Role-based access control and authentication

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM with PostgreSQL
- **Alembic**: Database migrations
- **JWT**: Secure authentication
- **pytest**: Comprehensive testing suite

### Frontend  
- **React**: Modern UI framework
- **Redux Toolkit**: State management
- **Material-UI**: Component library
- **axios**: HTTP client

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mrdpol-core
```

2. Backend setup:
```bash
cd backend
pip install -r requirements.txt
# Update .env file with your database credentials
# Run migrations
alembic upgrade head
```

3. Frontend setup:
```bash
cd frontend  
npm install
npm start
```

### Database Setup

Create the database:
```bash
./scripts/init_db.sh
```

Initialize roles and admin user:
```bash
./scripts/init_roles.sh
```

Default admin credentials:
- Email: `admin@mrdpol.com`
- Password: `admin123`

## API Documentation

Once the backend is running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## License

This project is proprietary software. All rights reserved.