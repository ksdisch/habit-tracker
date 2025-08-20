# #!/usr/bin/env python
# from logic import morning_report
# from config import SETTINGS # Add this line

# if __name__ == "__main__":
#     print(morning_report())



# In scripts_report.py
import os
from logic import morning_report
from config import SETTINGS

def set_multiline_output(name, value):
    """
    Sets a multiline output variable for GitHub Actions.
    """
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f'{name}<<EOF\n')
        f.write(f'{value}\n')
        f.write('EOF\n')

if __name__ == "__main__":
    # Ensure script runs in the correct mode for consistency
    print(f"Report script starting in MODE: {SETTINGS.MODE}")

    # Generate the report text by calling the function from your logic file
    report_content = morning_report()
    
    print("--- Report Generated ---")
    print(report_content)
    print("------------------------")

    # Set the output for the email step. The name 'report' must match
    # what you use in the YAML file (steps.generate.outputs.report).
    set_multiline_output('report', report_content)
    print("Successfully set 'report' output for the next step.")