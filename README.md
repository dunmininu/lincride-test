# Dynamic Pricing API for LincRide :: Ride-Hailing App

This project implements a dynamic pricing algorithm for a ride-hailing app using Django and Django REST Framework. It calculates ride fares based on distance, traffic, demand, and time-of-day factors, using SQLite as the database and caching to improve performance.

## Setup

### Environment

This project uses Pipenv, but feel free to use your preferred virtual environment tool.

To set up with Pipenv:

```bash
pipenv install
pipenv shell
```

Alternatively, you can use:

```bash
make init
```

### Environment Variables

Create a `.env` file in the project root with:

```env
BASE_FARE=2.5
PER_KM_RATE=1.0
DEBUG=True
SECRET_KEY=your-secret-key
DJANGO_LOG_LEVEL=INFO
```

## Running the Application

Start the Django server with:

```bash
python manage.py runserver
```

Access the API at:

```
http://127.0.0.1:8000/api/calculate-fare/
```

## API Usage

Send a GET request with these query parameters:

- **distance** (float, required): Ride distance in km (0.1 - 100)
- **traffic_level** (string, optional): One of `low`, `normal`, or `high`
- **demand_level** (string, optional): One of `normal` or `peak`

Example:

```
GET /api/calculate-fare/?distance=10&traffic_level=high&demand_level=peak
```

## Running Tests

Run all tests with:

```bash
make test
```

## Notes

- **Caching:** Fare calculations are cached for 5 minutes to improve performance.
- **Middleware:** `ConditionalGetMiddleware` is enabled to optimize API responses.
