# FoodDelievery
FoodDelievery service that calculates the final delievery time for meals

## set local envinronment variables

### set up virtual environment
python3 -m pip install --user virtualenv
python3 -m venv venv-uplevel
source venv-uplevel/bin/activate

### install requirements
pip install -r requirements.txt

### Run the project
cd foody

./manage.py runserver

## Run the api
http://localhost:8000/api/v1/get-delivery-time/

### input

[{"orderId": 12, "meals": ["A", "A"], "distance": 5},
{"orderId": 21, "meals": ["A", "M"], "distance": 1},
{"orderId": 14, "meals": ["M", "M", "M", "M", "A", "A", "A"], "distance": 10},
{"orderId": 32, "meals": ["M"], "distance": 0.1},
{"orderId": 22, "meals": ["A"], "distance": 3}]

### Output
[
    {
        "message": "Order 12 will get delivered in 57 minutes"
    },
    {
        "message": "Order 21 will get delivered in 37 minutes"
    },
    {
        "message": "Order 14 is denied, because the restaurant cannot deliver it on time."
    },
    {
        "message": "Order 32 will get delivered in 29.8 minutes"
    },
    {
        "message": "Order 22 will get delivered in 70.8 minutes"
    }
]
