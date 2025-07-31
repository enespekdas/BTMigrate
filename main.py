import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import auth.auth  # login olur
from workflow.orchestrator import process_all_pam_rows

if __name__ == "__main__":
    process_all_pam_rows()
