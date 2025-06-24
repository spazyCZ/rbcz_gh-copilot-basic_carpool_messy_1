#!/usr/bin/env python3
# BAD: No proper entry point script structure

from app import app, load_data
import utils

# BAD: Side effects at module level
print("Starting parking reservation system...")
load_data()
utils.log_action("Application started")

# BAD: No error handling, no proper main guard
app.run(debug=True, port=5002)
