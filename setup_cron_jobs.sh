#!/bin/bash

# SmartBiller Cron Jobs Setup Script
# This script sets up automated tasks for monthly invoices and reminders

echo "Setting up SmartBiller automated tasks..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

# Create log directory
mkdir -p logs

# Create the cron job entries
CRON_JOBS=""

# Monthly invoices - run on the 1st of each month at 9:00 AM
CRON_JOBS+="0 9 1 * * cd $SCRIPT_DIR && $PYTHON_PATH run_scheduled_tasks.py monthly_invoices >> logs/monthly_invoices.log 2>&1\n"

# Late payment reminders - run daily at 10:00 AM (after the 5th of each month)
CRON_JOBS+="0 10 * * * cd $SCRIPT_DIR && $PYTHON_PATH run_scheduled_tasks.py late_reminders >> logs/late_reminders.log 2>&1\n"

# Backup current crontab
echo "Backing up current crontab..."
crontab -l > crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# Add new cron jobs
echo "Adding SmartBiller cron jobs..."
echo -e "$CRON_JOBS" | crontab -

echo "Cron jobs have been set up successfully!"
echo ""
echo "Scheduled tasks:"
echo "1. Monthly Invoices: 1st of each month at 9:00 AM"
echo "2. Late Payment Reminders: Daily at 10:00 AM (active after 5th of month)"
echo ""
echo "Log files will be created in: $SCRIPT_DIR/logs/"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove all cron jobs: crontab -r"
echo ""
echo "To test the tasks manually:"
echo "  python3 run_scheduled_tasks.py monthly_invoices"
echo "  python3 run_scheduled_tasks.py late_reminders" 