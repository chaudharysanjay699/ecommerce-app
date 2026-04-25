# Database Backup API

This API provides endpoints for creating and downloading PostgreSQL database backups.

> **🔒 Super Admin Only**: All backup endpoints require super admin authentication (`is_super_admin=True`). Regular admin users (`is_admin=True`) cannot access these endpoints.

## Prerequisites

1. **Install PostgreSQL 16.3+ client tools** (for pg_dump):
   - **Windows**: Download from https://www.postgresql.org/download/windows/
     - Install PostgreSQL 16.3 or higher
     - Ensure the `bin` directory (e.g., `C:\Program Files\PostgreSQL\16\bin`) is added to your PATH
   - **Linux**: `sudo apt-get install postgresql-client-16`
   - **macOS**: `brew install postgresql@16`

2. **Verify pg_dump version** (should be 16.3 or higher):
   ```bash
   pg_dump --version
   ```
   Expected output: `pg_dump (PostgreSQL) 16.3` or higher

3. **Version Compatibility**: pg_dump must be the same or newer version than your PostgreSQL server. For PostgreSQL 16.x servers, use pg_dump 16.3+.

## Backup Features

This backup service is optimized for PostgreSQL 16.3+ with the following features:

1. **Automatic Cleanup**: Old backups are automatically deleted, keeping only the 10 most recent backups
2. **Timestamped Filenames**: Backups are named with timestamps like `backup_2026-04-22_10-30-45.sql`
3. **Security**: Only super-admin users can create/download backups
4. **Format**: Plain SQL format for easy inspection and restoration
5. **PostgreSQL 16.3+ Optimizations**:
   - Verbose logging for detailed progress tracking
   - Owner and privilege independence for portable backups
   - Quoted identifiers for better compatibility across PostgreSQL versions
   - `--clean` and `--if-exists` for safe database restores (DROP IF EXISTS before CREATE)
   - Lock wait timeout (30 seconds) to prevent indefinite blocking
   - 5-minute operation timeout to prevent hanging operations

## API Endpoints

### 1. Create and Download Backup (Recommended for React Button)

**Endpoint**: `POST /api/v1/admin/backup/create-and-download`

**Description**: Creates a backup and immediately returns it for download. Perfect for a "Backup" button in your React admin panel.

**Authentication**: Requires **super admin** token (only users with `is_super_admin=True`)

**Response**: SQL file download

**React Example**:
```jsx
import axios from 'axios';

const handleBackupClick = async () => {
  try {
    const response = await axios.post(
      '/api/v1/admin/backup/create-and-download',
      null,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        responseType: 'blob', // Important for file download
      }
    );

    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from Content-Disposition header or use default
    const contentDisposition = response.headers['content-disposition'];
    const filename = contentDisposition
      ? contentDisposition.split('filename=')[1].replace(/"/g, '')
      : `backup_${new Date().toISOString()}.sql`;
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    // Clean up the URL object
    window.URL.revokeObjectURL(url);
    
    alert('Backup downloaded successfully!');
  } catch (error) {
    console.error('Backup failed:', error);
    // Handle 403 error for non-super admin users
    if (error.response?.status === 403) {
      alert('Access denied: Super admin privileges required');
    } else {
      alert(`Backup failed: ${error.response?.data?.detail || error.message}`);
    }
  }
};

// Usage in component - Only show button for super admin users
// Assuming you have user data in context/state
const { user } = useAuth(); // or however you access user data

{user?.is_super_admin && (
  <button onClick={handleBackupClick} className="btn btn-primary">
    <i className="fas fa-download"></i> Backup Database
  </button>
)}
```

---

### 2. Create Backup (Without Download)

**Endpoint**: `POST /api/v1/admin/backup/create`

**Description**: Creates a backup and stores it on the server. Returns backup details without downloading.

**Authentication**: Requires **super admin** token (only users with `is_super_admin=True`)

**Query Parameters**:
- `backup_name` (optional): Custom name for the backup file

**Example**:
```javascript
const createBackup = async (customName = null) => {
  try {
    const response = await axios.post(
      '/api/v1/admin/backup/create',
      null,
      {
        params: customName ? { backup_name: customName } : {},
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    console.log('Backup created:', response.data);
    // {
    //   "filename": "backup_2026-04-22_10-30-45.sql",
    //   "file_path": "backups/backup_2026-04-22_10-30-45.sql",
    //   "file_size": 524288,
    //   "created_at": "2026-04-22T10:30:45.123456Z"
    // }
  } catch (error) {
    console.error('Backup creation failed:', error);
  }
};
```

---

### 3. List All Backups

**Endpoint**: `GET /api/v1/admin/backup/list`

**Description**: Get a list of all backup files stored on the server.

**Authentication**: Requires **super admin** token (only users with `is_super_admin=True`)

**Example**:
```javascript
const listBackups = async () => {
  try {
    const response = await axios.get('/api/v1/admin/backup/list', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    console.log('Available backups:', response.data);
    // {
    //   "backups": [
    //     {
    //       "filename": "backup_2026-04-22_10-30-45.sql",
    //       "file_path": "backups/backup_2026-04-22_10-30-45.sql",
    //       "file_size": 524288,
    //       "created_at": "2026-04-22T10:30:45.123456Z"
    //     }
    //   ],
    //   "total_count": 1
    // }
  } catch (error) {
    console.error('Failed to list backups:', error);
  }
};
```

---

### 4. Download Existing Backup

**Endpoint**: `GET /api/v1/admin/backup/download/{filename}`

**Description**: Download a previously created backup file.

**Authentication**: Requires **super admin** token (only users with `is_super_admin=True`)

**Path Parameters**:
- `filename`: Name of the backup file to download

**Example**:
```javascript
const downloadBackup = async (filename) => {
  try {
    const response = await axios.get(
      `/api/v1/admin/backup/download/${filename}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        responseType: 'blob',
      }
    );

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
  }
};
```

---

## Complete React Component Example

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DatabaseBackup = ({ user }) => { // Pass user prop with is_super_admin flag
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');

  const axiosConfig = {
    headers: { 'Authorization': `Bearer ${token}` }
  };

  // Only fetch backups if user is super admin
  useEffect(() => {
    if (user?.is_super_admin) {
      fetchBackups();
    }
  }, [user]);

  const fetchBackups = async () => {
    try {
      const response = await axios.get('/api/v1/admin/backup/list', axiosConfig);
      setBackups(response.data.backups);
    } catch (error) {
      console.error('Failed to fetch backups:', error);
      if (error.response?.status === 403) {
        alert('Access denied: Super admin privileges required');
      }
    }
  };

  const handleCreateAndDownload = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        '/api/v1/admin/backup/create-and-download',
        null,
        {
          ...axiosConfig,
          responseType: 'blob',
        }
      );

      // Download the file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const contentDisposition = response.headers['content-disposition'];
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `backup_${new Date().toISOString()}.sql`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      alert('Backup downloaded successfully!');
      
      // Refresh the list
      await fetchBackups();
    } catch (error) {
      console.error('Backup failed:', error);
      if (error.response?.status === 403) {
        alert('Access denied: Super admin privileges required');
      } else {
        alert(`Backup failed: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (filename) => {
    try {
      const response = await axios.get(
        `/api/v1/admin/backup/download/${filename}`,
        {
          ...axiosConfig,
          responseType: 'blob',
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      if (error.response?.status === 403) {
        alert('Access denied: Super admin privileges required');
      } else {
        alert('Download failed: ' + error.message);
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString();
  };

  // Only render if user is super admin
  if (!user?.is_super_admin) {
    return (
      <div className="database-backup">
        <div className="alert alert-warning">
          <p>🔒 Database backup is only available to super admin users.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="database-backup">
      <div className="header">
        <h2>Database Backup</h2>
        <button 
          onClick={handleCreateAndDownload} 
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Creating Backup...' : 'Create & Download Backup'}
        </button>
      </div>

      <div className="backup-list">
        <h3>Available Backups</h3>
        {backups.length === 0 ? (
          <p>No backups available.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Size</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {backups.map((backup) => (
                <tr key={backup.filename}>
                  <td>{backup.filename}</td>
                  <td>{formatFileSize(backup.file_size)}</td>
                  <td>{formatDate(backup.created_at)}</td>
                  <td>
                    <button
                      onClick={() => handleDownload(backup.filename)}
                      className="btn btn-sm btn-secondary"
                    >
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DatabaseBackup;
```

---

## Restoring a Backup

The backup files are created with PostgreSQL 16.3+ options for safe and portable restores.

**Important**: Backups include `DROP IF EXISTS` statements before CREATE statements, which means:
- You can safely restore to an existing database
- Existing objects will be dropped and recreated
- Make sure you have a backup before restoring!

To restore a backup, use the `psql` command:

```bash
# Basic restore
psql -h your-host -U your-user -d your-database -f backup_2026-04-22_10-30-45.sql

# With connection string
psql postgresql://user:password@host:5432/database -f backup_2026-04-22_10-30-45.sql

# For PostgreSQL 16.3+, you can also use verbose mode to see progress
psql -h your-host -U your-user -d your-database -f backup_2026-04-22_10-30-45.sql -v ON_ERROR_STOP=1
```

**Note**: The backup includes `DROP IF EXISTS` statements, so existing database objects will be safely dropped and recreated during restore.

---

## Troubleshooting

### Error: "pg_dump is not installed or not in PATH"
**Solution**: Install PostgreSQL 16.3+ client tools and ensure pg_dump is in your PATH.
- Windows: Add PostgreSQL bin directory to PATH (e.g., `C:\Program Files\PostgreSQL\16\bin`)
- Linux: `which pg_dump` should return a path
- Restart your terminal/IDE after PATH changes

### Error: "pg_dump version mismatch"
**Solution**: Your pg_dump version must match or exceed your PostgreSQL server version.
- Check versions: `pg_dump --version` vs your database server version
- For PostgreSQL 16.x servers, install pg_dump 16.3 or higher
- Upgrade PostgreSQL client tools to match your server version

### Error: "Database authentication failed"
**Solution**: Check your DATABASE_URL in the .env file has correct credentials.
```bash
# Verify connection manually
psql postgresql://user:password@host:5432/database -c "SELECT version();"
```

### Error: "Could not connect to database server"
**Solution**: 
- Verify the database host and port are correct and accessible from your server
- Check if database is running: `pg_isready -h host -p 5432`
- Check firewall/security group rules allow connections on port 5432

### Error: "Backup operation timed out after 5 minutes"
**Solution**: 
- The database may be under heavy load or very large
- Try again during off-peak hours
- For very large databases, consider increasing the timeout or using compressed format
- Check database performance: `SELECT * FROM pg_stat_activity;`

### Error: "Backup failed due to timeout or lock wait"
**Solution**:
- The backup waits max 30 seconds for table locks
- Active long-running transactions can block pg_dump
- Wait for transactions to complete or retry later
- Check for blocking queries: `SELECT * FROM pg_stat_activity WHERE wait_event_type = 'Lock';`

### Error: "Permission denied"
**Solutions**:
- Ensure the `backups/` directory exists and is writable by the application
- Database user needs SELECT privilege on all tables
- Check file system permissions: `ls -la backups/`

---

## Security Considerations

1. **Access Control**: Only authenticated **super admin** users (with `is_super_admin=True`) can access backup endpoints
2. **Path Traversal Protection**: The service validates filenames to prevent directory traversal attacks
3. **Automatic Cleanup**: Old backups are automatically removed (keeps 10 most recent) to prevent disk space issues
4. **Credential Security**: Database passwords are passed securely via environment variables (`PGPASSWORD`), not command-line arguments
5. **Lock Wait Timeout**: 30-second lock wait timeout prevents indefinite blocking
6. **Operation Timeout**: 5-minute timeout prevents hanging operations

---

## Notes

- Backups are stored in the `backups/` directory in your project root
- The system automatically keeps only the 10 most recent backups
- Backup files are in plain SQL format (.sql) with PostgreSQL 16.3+ optimizations
- Backups use `--no-owner` and `--no-privileges` flags for portable restores across different PostgreSQL instances
- All identifiers are quoted (`--quote-all-identifiers`) for maximum compatibility
- Backups include `--clean` and `--if-exists` for safe restores: `DROP IF EXISTS` statements before CREATE statements
- For large databases (>1GB), consider using compressed custom format:
  - Change `-F p` to `-F c` in the backup service code
  - Restore with `pg_restore` instead of `psql`
  
---

## Advanced Options

### Using Compressed Format for Large Databases

For databases larger than 1GB, you might want to use compressed custom format:

1. Edit `app/services/backup_service.py`
2. Change `"-F", "p"` to `"-F", "c"` in the pg_dump command
3. Backups will have better compression but require `pg_restore` to restore:

```bash
# Restore custom format backup
pg_restore -h your-host -U your-user -d your-database backup_2026-04-22_10-30-45.sql

# With verbose and clean options
pg_restore -h your-host -U your-user -d your-database -v -c backup_2026-04-22_10-30-45.sql
```
