# WedCraft - Wedding Website Builder

A comprehensive wedding website builder with FastAPI backend and database connectivity, featuring user and admin authentication with role-based access control.

## Features

- 🔐 **Dual Authentication System**: Separate login for users and admins
- 👥 **Role-Based Access**: Admin and User roles with different permissions
- 💾 **Database Integration**: SQLite database with SQLAlchemy ORM
- 📊 **Admin Dashboard**: Complete management interface for users, events, and RSVP responses
- 🎨 **Modern UI**: Beautiful, responsive design with glassmorphism effects
- 📱 **Mobile Friendly**: Fully responsive design for all devices

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT tokens with bcrypt password hashing
- **UI Framework**: Custom CSS with modern design patterns

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Clone or download the project files**
2. **Run the startup script**:
   ```bash
   python start_server.py
   ```
   This will automatically:
   - Install all dependencies
   - Initialize the database with sample data
   - Start the FastAPI server

### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```bash
   python init_db.py
   ```

3. **Start the server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Access the Application

Once the server is running, you can access:

- **Main Application**: http://localhost:8000
- **Login Page**: http://localhost:8000/login.html
- **Dashboard**: http://localhost:8000/dashboard.html
- **API Documentation**: http://localhost:8000/docs

## Default Login Credentials

### Admin Access
- **Email**: `admin@wedcraft.com`
- **Password**: `admin123`
- **Permissions**: Full access to all features

### Sample User Accounts
- **Couple**: `john.sarah@example.com` / `password123`
- **Planner**: `planner@example.com` / `planner123`
- **Vendor**: `vendor@example.com` / `vendor123`

## Database Schema

### Users Table
- User management with roles (couple, planner, vendor)
- Encrypted password storage
- Wedding date tracking

### Admins Table
- Separate admin user management
- Admin-specific permissions

### Events Table
- Wedding event details
- Bride and groom information
- Location and date management

### RSVP Responses Table
- Guest response tracking
- Attendance and food preferences
- Family member counts

## API Endpoints

### Authentication
- `POST /api/user/login` - User login
- `POST /api/admin/login` - Admin login

### User Management (Admin Only)
- `GET /api/admin/users` - List all users
- `POST /api/admin/create-user` - Create new user
- `GET /api/admin/admins` - List all admins

### Event Management
- `GET /api/admin/events` - List all events
- `POST /api/admin/create-event` - Create new event

### RSVP Management
- `GET /api/admin/rsvp-responses` - List all RSVP responses
- `POST /api/rsvp/submit` - Submit RSVP response

### Dashboard Stats
- `GET /api/admin/stats` - Get dashboard statistics

## Role-Based Access Control

### Admin Users
- Full access to dashboard
- User management capabilities
- Event creation and management
- RSVP response viewing
- System statistics

### Regular Users
- Limited dashboard access
- View-only permissions for most features
- Cannot create or delete users/events

## File Structure

```
wedcraft/
├── main.py                 # FastAPI application
├── init_db.py             # Database initialization script
├── start_server.py        # Automated startup script
├── requirements.txt       # Python dependencies
├── login.html            # Login page
├── dashboard.html        # Admin/User dashboard
├── assets/               # Static assets (images, etc.)
├── wedcrafts            # MySQL database (create manually)
└── README.md            # This file
```

## Development

### Adding New Features

1. **Database Changes**: Modify models in `main.py` and run database migrations
2. **API Endpoints**: Add new routes in `main.py`
3. **Frontend**: Update HTML/CSS/JavaScript in respective files

### Security Considerations

- Change the `SECRET_KEY` in `main.py` for production
- Use environment variables for sensitive configuration
- Implement proper HTTPS in production
- Consider rate limiting for API endpoints

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port in `start_server.py` or `main.py`
2. **Database Errors**: Ensure MySQL is running and the `wedcrafts` database exists, then run `python init_db.py` again
3. **Permission Errors**: Ensure you have write permissions in the project directory
4. **MySQL Connection Errors**: Check MySQL credentials in the connection string and ensure MySQL service is running

### Logs and Debugging

- Check console output for error messages
- Use the FastAPI automatic documentation at `/docs` for API testing
- Enable debug mode by setting `debug=True` in uvicorn configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check console logs for error details

---

**Happy Wedding Planning! 💒✨**