#!/usr/bin/env python
# Simulate past days of habit completions in the local DB.
from simulate import simulate_past_days

if __name__ == "__main__":
    simulate_past_days(7)
    print("Simulated 7 days.")
