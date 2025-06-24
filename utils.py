# BAD: Utility functions mixed with business logic, no proper module structure
import random
import string

# BAD: Global variables in utility file
CONFIG = {
    "spots": ["A1", "A2", "A3", "B1", "B2", "B3"],
    "admin_pass": "admin123"
}

# BAD: Overly complex function for simple task
def generate_random_string():
    chars = string.ascii_letters + string.digits
    result = ""
    for i in range(10):
        result += random.choice(chars)
    return result

# BAD: Function name doesn't match what it does
def validate_user_input(input_data):
    # BAD: No actual validation, just returns True
    return True

# BAD: Hardcoded values, no error handling
def get_parking_spots():
    spots = CONFIG["spots"]
    return spots

# BAD: Function with side effects
def log_action(action):
    with open("log.txt", "a") as f:
        f.write(f"{action}\n")
    print(f"Logged: {action}")  # BAD: Print statements in production code
