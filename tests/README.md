# Tests and Utility Scripts

This folder contains all test scripts, utility scripts, and development tools for the Food Safety Agency Inspection System.

## Contents

This folder includes:

- **Test Scripts**: Scripts to test various functionality (test_*.py)
- **Check Scripts**: Scripts to verify data and system state (check_*.py)
- **Analysis Scripts**: Scripts to analyze data and generate reports (analyze_*.py)
- **Sync Scripts**: Scripts for data synchronization (sync_*.py)
- **Restore/Backup Scripts**: Scripts for data restoration (restore_*.py, master_*.py)
- **User Management Scripts**: Scripts for managing users (change_*.py, create_*.py)
- **Utility Scripts**: Miscellaneous utility scripts
- **Test Databases**: SQLite test databases (*.sqlite3)
- **Test Data**: JSON and HTML test files

## Running Scripts

Most scripts can be run directly from the command line:

```bash
cd /path/to/project
python tests/script_name.py
```

Some scripts may require Django to be set up and will automatically configure the Django environment.

## Important Scripts

### Data Compliance
- `test_inspection_compliance.py` - Comprehensive test to verify inspection data integrity

### Data Analysis
- `analyze_*.py` - Various data analysis scripts
- `check_*.py` - Data verification and validation scripts

### User Management
- `change_user_password.py` - Change user passwords
- `change_user_role.py` - Change user roles
- `create_*.py` - Create various entities

### Data Sync
- `sync_*.py` - Data synchronization scripts
- `restore_*.py` - Data restoration scripts

## Note

These scripts are for development, testing, and maintenance purposes. They should not be run in production without careful review and understanding of what they do.
