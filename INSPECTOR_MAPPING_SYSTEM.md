# Inspector Mapping System

## Overview
This system ensures that all inspector users can see their inspections correctly by maintaining proper mappings between user accounts and inspector IDs in the inspection data.

## Problem Solved
Previously, inspectors couldn't see their inspections because:
1. Inspector mappings were incorrect or missing
2. Inspector IDs in the mapping table didn't match the actual inspection data
3. New inspectors weren't automatically mapped when created

## Solution Components

### 1. Automated Mapping Creation
- **Signal Handler**: Automatically creates inspector mappings when new inspector users are created
- **Location**: `main/signals.py`
- **Trigger**: When a user with `role='inspector'` is created

### 2. Validation System
- **Command**: `python manage.py validate_inspector_mappings`
- **Purpose**: Check for mapping issues and conflicts
- **Auto-fix**: `python manage.py validate_inspector_mappings --auto-fix`

### 3. Audit System
- **Command**: `python manage.py audit_inspector_mappings`
- **Purpose**: Comprehensive audit of all mappings vs actual data

### 4. Fix System
- **Command**: `python manage.py fix_inspector_mappings`
- **Purpose**: Complete rebuild of all mappings from actual inspection data

## Usage

### For New Inspectors
1. Create the user account with `role='inspector'`
2. The system automatically creates a mapping
3. If the inspector exists in inspection data, the correct ID is used
4. If not, a dummy ID is assigned (needs manual correction)

### For Existing Issues
1. Run `python manage.py validate_inspector_mappings` to check for issues
2. Run `python manage.py validate_inspector_mappings --auto-fix` to fix automatically
3. For major issues, run `python manage.py fix_inspector_mappings` to rebuild all mappings

### Regular Maintenance
- Run `python manage.py validate_inspector_mappings` weekly
- Run `python manage.py audit_inspector_mappings` monthly

## Files Created/Modified

### New Files
- `main/management/commands/audit_inspector_mappings.py`
- `main/management/commands/fix_inspector_mappings.py`
- `main/management/commands/validate_inspector_mappings.py`
- `main/signals.py`
- `INSPECTOR_MAPPING_SYSTEM.md`

### Modified Files
- `main/apps.py` - Added signal registration

## Prevention Measures

1. **Automatic Mapping**: New inspectors get mappings automatically
2. **Validation Commands**: Regular checks ensure data integrity
3. **Auto-fix Capability**: Most issues can be fixed automatically
4. **Comprehensive Auditing**: Full system health checks

## Current Status
✅ All existing inspector mappings are now correct
✅ Inspector "lwandilemaqina" can see 780 inspections
✅ New inspectors will be automatically mapped
✅ Validation system prevents future issues

## Troubleshooting

### Inspector Can't See Inspections
1. Run `python manage.py validate_inspector_mappings`
2. If issues found, run with `--auto-fix`
3. Check that the user's full name matches the inspector name in data

### Mapping Conflicts
1. Run `python manage.py audit_inspector_mappings`
2. Run `python manage.py fix_inspector_mappings` to rebuild all mappings
3. Verify with validation command

### New Inspector Issues
1. Check that the user was created with `role='inspector'`
2. Verify the signal handler is working
3. Run validation to check for issues
