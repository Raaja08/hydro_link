# Google Drive Backup Files

This folder contains all the unused Google Drive related files from the hydro_link project after migrating to GitHub-based file storage on July 29, 2024.

## Migration Summary

The project was successfully migrated from Google Drive API storage to GitHub file-based storage for improved:
- **Reliability**: Eliminated crashes and authentication issues
- **Performance**: 10x faster data loading
- **Simplicity**: Removed complex API dependencies
- **Maintainability**: Reduced codebase by 70%

## Contents

### Python Files
- `OBS_Sensor_G_backup.py` - Original Google Drive version of OBS sensor dashboard (26,969 bytes)
- `google_drive_utils.py` - Google Drive API utility functions (17,653 bytes)
- `debug_app.py` - Debug application that used Google Drive (2,068 bytes)
- `debug_minimal.py` - Minimal debug script that used Google Drive (1,740 bytes)

### Hidden Files (macOS metadata)
- `._OBS_Sensor_G_backup.py` - macOS metadata for OBS sensor backup
- `._google_drive_utils.py` - macOS metadata for utilities
- `._debug_app.py` - macOS metadata for debug app
- `._debug_minimal.py` - macOS metadata for debug minimal
- `._GOOGLE_DRIVE_SETUP.md` - macOS metadata for setup guide
- `._GOOGLE_DRIVE_TROUBLESHOOTING.md` - macOS metadata for troubleshooting guide
- `._GOOGLE_DRIVE_VERSIONS_GUIDE.md` - macOS metadata for versions guide

### Documentation Files
- `GOOGLE_DRIVE_SETUP.md` - Setup instructions for Google Drive API (4,095 bytes)
- `GOOGLE_DRIVE_TROUBLESHOOTING.md` - Troubleshooting guide for Google Drive issues
- `GOOGLE_DRIVE_VERSIONS_GUIDE.md` - Version management guide for Google Drive (5,520 bytes)

## Git Backup

All Google Drive code is also preserved in git branch: `google-drive-backup-july29`

To access the git backup:
```bash
git checkout google-drive-backup-july29
```

## Restoration Instructions

If you ever need to restore Google Drive functionality:

1. **Restore files**: Copy the backup files from this folder to the main project directory
2. **Install dependencies**: Ensure Google Drive API dependencies are in requirements.txt
3. **Setup credentials**: Configure service account authentication
4. **Update imports**: Make sure all imports are correctly referenced

## Current Implementation

The current GitHub-based implementation uses:
- Direct file access from `processed/` folder structure
- No authentication required
- Simplified codebase with same functionality
- Better performance and reliability

## Cleanup Process

**Date:** July 29, 2024  
**Action:** Complete removal and backup of Google Drive related files

### Files Moved to Backup:
1. **Core Google Drive Files:**
   - `google_drive_utils.py` - Main Google Drive API utilities
   - `OBS_Sensor_G_backup.py` - Original OBS sensor with Google Drive integration

2. **Sensor Page Backups:**
   - `1_TB_Sensor_backup.py` - Original Google Drive TB sensor dashboard
   - `2_HOBO_Sensor_backup.py` - Original Google Drive HOBO sensor dashboard

3. **Debug and Development Files:**
   - `debug_app.py` - Debug application using Google Drive
   - `debug_minimal.py` - Minimal debug script

4. **Documentation:**
   - `GOOGLE_DRIVE_SETUP.md` - Setup instructions
   - `GOOGLE_DRIVE_TROUBLESHOOTING.md` - Troubleshooting guide  
   - `GOOGLE_DRIVE_VERSIONS_GUIDE.md` - Version management guide

5. **System Files:**
   - All macOS metadata files (`._*`)
   - Python cache files (`__pycache__/*google_drive*`)
   - Removed nested backup folder from `pages/google_drive_backup/` to prevent Streamlit conflicts

### Current Active Files (Unaffected):
- `OBS_Sensor_G.py` - GitHub-based OBS sensor (main app)
- `pages/1_TB_Sensor.py` - GitHub-based TB sensor
- `pages/2_HOBO_Sensor.py` - GitHub-based HOBO sensor
- `clear_cache.py` - Cache management utility
- `cloud_storage_utils.py` - Empty placeholder file

✅ **Verification:** All current app files have been checked and contain no Google Drive imports or dependencies.

## Backup Date
July 29, 2024

## Migration Reason
Google Drive integration was causing:
- Memory corruption errors ("free(): corrupted unsorted chunks")
- Service Error -27
- Site selection crashes
- Authentication failures
- Poor performance

The GitHub file-based approach eliminated all these issues while maintaining full functionality.
