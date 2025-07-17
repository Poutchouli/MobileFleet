# Mobile Fleet Management System

A comprehensive fleet management application built with Flask and PostgreSQL for managing mobile devices, workers, and support tickets.

## Features

- **Role-based Access Control**: Administrator, Manager, and Support roles
- **Device Management**: Track phones, SIM cards, and assignments
- **Worker Management**: Manage workers across different sectors
- **Support Ticket System**: Create and track support tickets for device issues
- **Responsive Dashboard**: Modern UI with custom CSS and Tailwind CSS

## Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MobileFleet
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Database

The application uses PostgreSQL running in a Docker container. To start the database:

```bash
# Start the database container
docker-compose up -d db

# Wait a few seconds for the database to initialize
# The database will be available on port 5433
```

### 4. Initialize the Database

Run the database initialization script to create tables and populate sample data:

```bash
# Set the database URL environment variable
$env:DATABASE_URL="dbname=fleet_db user=postgres password=password host=localhost port=5433"

# Initialize the database
python init_database.py
```

### 5. Start the Flask Application

```bash
# The .env file already contains the correct DATABASE_URL
python app.py
```

The application will be available at `http://localhost:5000`

## Default User Accounts

The database initialization creates the following test users:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `adminpass` | Administrator | Full system access |
| `manager_north` | `managerpass` | Manager | Manages Northern Sector |
| `manager_south` | `managerpass` | Manager | Manages Southern Sector |
| `support_tech` | `supportpass` | Support | Handles support tickets |
| `support_junior` | `supportpass` | Support | Junior support technician |

## Database Configuration

The application uses the following database configuration:

- **Host**: localhost
- **Port**: 5433 (mapped from container port 5432)
- **Database**: fleet_db
- **Username**: postgres
- **Password**: password

These settings are configured in:
- `docker-compose.yml` (for containerized setup)
- `.env` file (for local development)

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. **Check if the database container is running**:
   ```bash
   docker-compose ps
   ```

2. **Restart the database container**:
   ```bash
   docker-compose down
   docker-compose up -d db
   ```

3. **Verify the database is accessible**:
   ```bash
   docker exec -it fleet_db psql -U postgres -d fleet_db -c "SELECT COUNT(*) FROM users;"
   ```

### Re-initializing the Database

To completely reset the database:

```bash
# Stop and remove the database container
docker-compose down

# Remove the database volume (this will delete all data)
docker volume rm mobilefleet_postgres_data

# Start the database container again
docker-compose up -d db

# Re-initialize the database
python init_database.py
```

### Environment Variables

Make sure the following environment variables are set:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5433/fleet_db
FLASK_ENV=development
FLASK_DEBUG=True
```

## Development

### Running with Docker Compose

For a complete containerized setup:

```bash
# Build and start all services
docker-compose up --build

# The application will be available at http://localhost:5000
# Database initialization happens automatically
```

### Project Structure

```
MobileFleet/
├── app.py                 # Main Flask application
├── init_database.py       # Database initialization script
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Flask app container
├── .env                  # Environment variables
├── static/
│   └── css/
│       └── custom.css    # Custom styling
└── templates/
    ├── base.html         # Base template
    ├── admin/            # Administrator templates
    ├── manager/          # Manager templates
    ├── support/          # Support templates
    └── components/       # Reusable components
```

## API Endpoints

The application provides RESTful API endpoints for:

- **Authentication**: Login/logout functionality
- **User Management**: CRUD operations for users
- **Role Management**: Role configuration
- **Device Management**: Phone and SIM card management
- **Ticket Management**: Support ticket system
- **Manager API**: Team status and ticket creation
- **Support API**: Active ticket management

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Tailwind CSS + Custom CSS
- **Authentication**: Session-based with password hashing
- **Containerization**: Docker & Docker Compose

## License

This project is for educational and demonstration purposes.
