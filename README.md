# Carbon Footprint Tracker for Households

A comprehensive web application built with Django and Bootstrap that helps households measure, track, and reduce their carbon footprint through detailed monitoring of energy usage, transportation, and dietary habits.

## 🌱 Features

### Core Functionality
- **Household Management**: Create and manage multiple households with multiple members
- **Carbon Footprint Calculation**: Automated calculation of CO₂ emissions based on:
  - Energy usage (electricity, gas, oil, renewables)
  - Transportation (cars, public transport, flights, cycling)
  - Diet (meat consumption, local/organic food choices)
- **Real-time Dashboard**: Interactive dashboard with visualizations and metrics
- **Personalized Recommendations**: AI-driven tips for reducing carbon footprint
- **Progress Tracking**: Historical data and trend analysis
- **Goal Setting**: Set and track reduction goals

### Technical Features
- **REST API**: Full RESTful API for all data operations
- **Responsive Design**: Bootstrap 5-based UI that works on all devices
- **Data Visualization**: Interactive charts using Chart.js
- **User Authentication**: Secure user registration and login
- **Admin Interface**: Django admin for data management
- **Extensible Architecture**: Easy to add new emission factors and categories

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd carbon-footprint-tracker
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Populate initial data:**
   ```bash
   python manage.py populate_data
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Web Interface: http://127.0.0.1:8000/
   - Admin Interface: http://127.0.0.1:8000/admin/
   - API Documentation: http://127.0.0.1:8000/api/

## 📊 Usage Guide

### Getting Started
1. **Register**: Create a new account or login with existing credentials
2. **Create Household**: Set up your first household with basic information
3. **Add Data**: Start recording your energy usage, transportation, and diet data
4. **View Dashboard**: Monitor your carbon footprint and get personalized recommendations

### Data Entry
- **Energy Usage**: Record monthly utility bills and energy consumption
- **Transportation**: Log daily commutes, trips, and travel patterns
- **Diet**: Track weekly food consumption by category

### Understanding Your Footprint
- **Total Emissions**: Annual CO₂ equivalent in kilograms
- **Per Capita**: Emissions divided by household members
- **Category Breakdown**: See which areas contribute most to your footprint
- **Comparisons**: Compare against national and global averages

## 🛠️ API Documentation

### Authentication
All API endpoints require authentication. Use session-based authentication or obtain an API token.

### Main Endpoints

#### Households
- `GET /api/households/` - List user's households
- `POST /api/households/` - Create new household
- `GET /api/households/{id}/` - Get household details
- `GET /api/households/{id}/footprint_summary/` - Get carbon footprint summary

#### Data Entry
- `POST /api/energy-usage/` - Add energy usage data
- `POST /api/transportation/` - Add transportation data
- `POST /api/diet/` - Add diet data

#### Carbon Footprint
- `GET /api/carbon-footprints/` - List footprint calculations
- `POST /api/carbon-footprints/calculate/` - Calculate footprint for household

#### Reduction Tips
- `GET /api/reduction-tips/` - List all reduction tips
- `GET /api/reduction-tips/personalized/` - Get personalized tips

## 🏗️ Architecture

### Backend (Django)
- **Models**: Comprehensive data models for households, emissions, and recommendations
- **Services**: Business logic for carbon footprint calculations
- **API**: Django REST Framework for API endpoints
- **Admin**: Django admin interface for data management

### Frontend (Bootstrap + JavaScript)
- **Responsive Design**: Mobile-first Bootstrap 5 interface
- **Interactive Charts**: Chart.js for data visualization
- **AJAX Integration**: Seamless API integration without page reloads

### Database
- **SQLite**: Default database for development
- **PostgreSQL**: Recommended for production
- **Migrations**: Django migrations for schema management

## 🌍 Environmental Impact

### Emission Factors
The application uses scientifically-backed emission factors:
- **Energy**: Based on regional electricity grid mix and fuel types
- **Transportation**: EPA and IPCC guidelines for different vehicle types
- **Diet**: Lifecycle analysis of food production and transportation

### Accuracy
- Calculations are estimates based on averages and user input
- Results provide relative comparisons and trend analysis
- For precise measurements, consider professional energy audits

## 🔧 Configuration

### Settings
Key settings in `carbon_tracker/settings.py`:
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Configure for your domain
- `DATABASES`: Configure database connection
- `STATIC_ROOT`: Set for static file serving

### Environment Variables
Create a `.env` file for sensitive settings:
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=your-database-url
```

## 📈 Data Visualization

The application includes several types of visualizations:
- **Pie Charts**: Emission breakdown by category
- **Line Charts**: Trends over time
- **Bar Charts**: Comparisons with averages
- **Progress Bars**: Goal achievement tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python manage.py test

# Check code style
flake8 .

# Run development server with debug
python manage.py runserver --settings=carbon_tracker.settings_dev
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests via GitHub issues
- **Admin Interface**: Use Django admin for data management
- **API**: Test endpoints using the browsable API interface

## 🔮 Future Enhancements

- **Mobile App**: Native mobile applications
- **IoT Integration**: Smart home device integration
- **Social Features**: Community challenges and comparisons
- **Advanced Analytics**: Machine learning predictions
- **Carbon Offsetting**: Integration with offset providers
- **External APIs**: Real-time energy and transportation data

## 📊 Sample Data

The application comes with sample reduction tips and emission factors. To add your own:

1. Use the Django admin interface
2. Use the management command: `python manage.py populate_data`
3. Use the API endpoints to programmatically add data

---

**Making a difference, one household at a time! 🌱**