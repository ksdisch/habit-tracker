# from __future__ import annotations
# import datetime as dt
# from db import connect, upsert_habit, write_log
# from config import SETTINGS # Add this line


# print(f"Script starting in MODE: {SETTINGS.MODE}")

# # You likely have a main function or block of code that runs
# if SETTINGS.MODE == "LIVE":
#     print("SCRIPT TRACE: Running in LIVE mode.")
    
#     # 1. Check if you are getting data from Todoist
#     print("SCRIPT TRACE: Fetching data from Todoist API...")
#     data_from_api = your_todoist_fetching_function() # This is a placeholder
#     print(f"SCRIPT TRACE: Found {len(data_from_api)} items from API.")

#     # 2. Check if the script is trying to save the data
#     if data_from_api:
#         print("SCRIPT TRACE: Data found, attempting to save to database.")
#         your_database_saving_function(data_from_api) # Placeholder
#         print("SCRIPT TRACE: Finished database save attempt.")
#     else:
#         print("SCRIPT TRACE: No data from API, nothing to save.")
# else:
#     print("SCRIPT TRACE: Running in MOCK mode. Skipping live operations.")

# print("Script finished.")


# def simulate_past_days(days: int = 7) -> None:
#     fake = [("123", "Meditate"), ("456", "Read 15 minutes"), ("789", "Workout")]
#     start = dt.date.today() - dt.timedelta(days=days - 1)
#     with connect() as con:
#         for task_id, name in fake:
#             upsert_habit(con, task_id, name)
#         for i in range(days):
#             d = start + dt.timedelta(days=i)
#             for j, (task_id, _) in enumerate(fake):
#                 did = not ((d.day + j) % 2 == 0)
#                 write_log(con, d.isoformat(), task_id, did)



# from __future__ import annotations
# import datetime as dt

# # Import the functions and settings from your other files
# from config import SETTINGS
# from db import connect, upsert_habit, write_log
# from logic import get_and_log_habits
# from time_utils import ledger_date_with_cutoff


# def main():
#     """
#     Main function to run the nightly habit logging process.
#     """
#     print(f"Script starting in MODE: {SETTINGS.MODE}")

#     # Guard clause: If not in LIVE mode, do nothing and exit.
#     if SETTINGS.MODE != "LIVE":
#         print("SCRIPT TRACE: Not in LIVE mode. Skipping operations.")
#         print("Script finished.")
#         return

#     print("SCRIPT TRACE: Running in LIVE mode.")
    
#     # 1. Determine the correct date to log for based on the cutoff time.
#     log_date = ledger_date_with_cutoff(SETTINGS.TIMEZONE, SETTINGS.CUTOFF_HOUR)
#     print(f"SCRIPT TRACE: Determined the date to log for is {log_date.isoformat()}.")

#     # 2. Fetch habits and log them to the database.
#     try:
#         # get_and_log_habits will contain the logic to call the Todoist API
#         # and then write the results to the database.
#         completed_habits, incomplete_habits = get_and_log_habits(log_date)
        
#         print(f"SCRIPT TRACE: Successfully logged {len(completed_habits)} completed habits.")
#         print(f"SCRIPT TRACE: Found {len(incomplete_habits)} incomplete habits.")

#     except Exception as e:
#         # If anything goes wrong, print the error.
#         print(f"SCRIPT TRACE: An error occurred: {e}")

#     print("Script finished.")


# if __name__ == "__main__":
#     main()


from __future__ import annotations
from config import SETTINGS
from logic import nightly_live # Corrected import

def main():
    """
    Main function to run the nightly habit logging process.
    """
    print(f"Script starting in MODE: {SETTINGS.MODE}")

    if SETTINGS.MODE != "LIVE":
        print("SCRIPT TRACE: Not in LIVE mode. Skipping operations.")
        print("Script finished.")
        return

    print("SCRIPT TRACE: Running in LIVE mode.")
    
    try:
        # Call the correct function from logic.py
        nightly_live()
        print("SCRIPT TRACE: Nightly live function completed successfully.")
    except Exception as e:
        # If anything goes wrong, print the error.
        print(f"SCRIPT TRACE: An error occurred: {e}")

    print("Script finished.")


if __name__ == "__main__":
    main()