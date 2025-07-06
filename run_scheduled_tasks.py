#!/usr/bin/env python3
"""
CLI script to run scheduled tasks for SmartBiller
Usage:
    python run_scheduled_tasks.py monthly_invoices
    python run_scheduled_tasks.py late_reminders
    python run_scheduled_tasks.py all
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.scheduled_tasks import run_monthly_invoices, run_late_reminders

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_scheduled_tasks.py <task>")
        print("Tasks: monthly_invoices, late_reminders, all")
        sys.exit(1)
    
    task = sys.argv[1].lower()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print(f"Running scheduled task: {task}")
        print(f"Started at: {datetime.now()}")
        
        if task == "monthly_invoices":
            run_monthly_invoices()
        elif task == "late_reminders":
            run_late_reminders()
        elif task == "all":
            print("Running monthly invoices...")
            run_monthly_invoices()
            print("Running late payment reminders...")
            run_late_reminders()
        else:
            print(f"Unknown task: {task}")
            print("Available tasks: monthly_invoices, late_reminders, all")
            sys.exit(1)
        
        print(f"Completed at: {datetime.now()}")

if __name__ == "__main__":
    main() 