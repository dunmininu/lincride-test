# LincRide Dynamic Pricing API

> Smart, real-time fare calculations for modern ride-hailing

This API powers LincRide's dynamic pricing system, calculating fares based on key factors like distance, traffic conditions, demand levels, and time of day. Built with Django and Django REST Framework, it provides reliable and transparent pricing through an efficient SQLite database with performance-optimizing caches.

## Getting Started

### Setting Up Your Environment

The project supports flexible environment setup options:

```bash
# Using Pipenv (recommended)
pipenv install
pipenv shell

# Alternative quick setup
make init
```

### Environment Configuration

Create a `.env` file in your project root:

```env
BASE_FARE=2.5          # Base fare amount
PER_KM_RATE=1.0       # Per-kilometer rate
DEBUG=True            # Enable development mode
SECRET_KEY=your-secret-key
DJANGO_LOG_LEVEL=INFO
```

### Launch the API

Start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/calculate-fare/`

## API Reference

### Calculate Fare Endpoint

Send GET requests with the following parameters:

- `distance`: Ride distance in kilometers (0.1 - 100)
- `traffic_level`: Current traffic conditions (`low`, `normal`, `high`)
- `demand_level`: Demand status (`normal`, `peak`)

Example request:

```
GET /api/calculate-fare/?distance=10&traffic_level=high&demand_level=peak
```

## Development

### Running Tests

Execute the test suite:

```bash
make test
```

### Starting the server

```bash
make start
```

## Technical Notes

- Fare calculations are cached for 5 minutes to optimize performance
- Implements `ConditionalGetMiddleware` for efficient API responses
- Built on Django's robust REST framework for reliable API handling
