# Volume Management for Local Development

This directory contains bind mounts for container data, providing transparent access to persistent data during local development.

## Directory Structure

```
infrastructure/volumes/
├── postgresql/
│   └── data/          # PostgreSQL data files (gitignored)
├── redis/
│   └── data/          # Redis persistence files (gitignored)
└── n8n/
    └── data/          # n8n workflows and configuration (gitignored)
```

## Why Bind Mounts for Development?

### ✅ **Advantages of Local Bind Mounts**

#### **🔍 Transparency & Debugging**
- Direct access to database files for debugging
- Easy inspection of PostgreSQL logs and configuration
- Clear visibility of n8n workflow files
- Simple backup and restore operations

#### **🛠️ Development Benefits**
- **Easy Reset**: Delete specific service data without affecting others
- **Data Inspection**: Direct access to database files for troubleshooting  
- **Configuration Access**: Modify container configurations directly
- **Backup/Restore**: Simple copy operations for data management

#### **🎯 Development Workflow**
```bash
# Reset PostgreSQL data only
rm -rf infrastructure/volumes/postgresql/data/*

# Backup n8n workflows
cp -r infrastructure/volumes/n8n/data/ backups/n8n-$(date +%Y%m%d)/

# Inspect Redis data
ls -la infrastructure/volumes/redis/data/
```

### ⚠️ **Cross-Platform Considerations**

#### **Linux (Recommended)**
- ✅ **Native Performance**: Direct filesystem access
- ✅ **No Permission Issues**: Native user mapping
- ✅ **Optimal for Development**: Best performance and compatibility

#### **macOS**
- ⚠️ **Virtualization Overhead**: Docker Desktop runs in VM
- ✅ **Functional**: Works but with some performance impact
- 💡 **Tip**: For heavy database operations, consider named volumes in production

#### **Windows WSL2**
- ✅ **Good Performance**: WSL2 provides near-native performance
- ✅ **Linux Compatibility**: Same behavior as Linux
- 💡 **Tip**: Store project in WSL2 filesystem for best performance

## Volume Configuration

### **PostgreSQL**
```yaml
volumes:
  - ./volumes/postgresql/data:/var/lib/postgresql/data
```
- **Contains**: Database files, logs, configuration
- **Purpose**: Multi-tenant database with pgvector support
- **Access**: Database files directly accessible for backup/restore

### **Redis**
```yaml
volumes:
  - ./volumes/redis/data:/data
```
- **Contains**: RDB snapshots, AOF files
- **Purpose**: Session management, caching, pub/sub
- **Access**: Direct access to persistence files

### **n8n**
```yaml
volumes:
  - ./volumes/n8n/data:/home/node/.n8n
```
- **Contains**: Workflows, credentials, settings
- **Purpose**: SDLC automation workflows
- **Access**: Workflow files for version control and backup

## Data Management Commands

### **Fresh Start (All Services)**
```bash
# Stop services
cd infrastructure && podman-compose down

# Clean all data
rm -rf volumes/*/data/*

# Restart services (will recreate databases)
podman-compose up -d
```

### **Service-Specific Reset**
```bash
# Reset only PostgreSQL
podman-compose stop postgres
rm -rf volumes/postgresql/data/*
podman-compose start postgres

# Reset only n8n workflows
podman-compose stop n8n
rm -rf volumes/n8n/data/*
podman-compose start n8n
```

### **Backup Operations**
```bash
# Create timestamped backup
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup all volumes
cp -r infrastructure/volumes/ $BACKUP_DIR/

# Restore from backup
rm -rf infrastructure/volumes/
cp -r $BACKUP_DIR/volumes/ infrastructure/
```

## Git Integration

### **What's Tracked**
- ✅ **Directory Structure**: Empty volume directories
- ✅ **Documentation**: This README and setup scripts
- ✅ **Configuration**: containers-compose.yml volume mappings

### **What's Ignored**
- ❌ **Data Files**: All files in `data/` subdirectories
- ❌ **Logs**: Container-generated log files
- ❌ **Temporary Files**: Runtime and cache files

### **.gitignore Configuration**
```gitignore
# Volume bind mounts (local development data)
infrastructure/volumes/postgresql/data/
infrastructure/volumes/redis/data/
infrastructure/volumes/n8n/data/
```

## Migration to Production

When moving to production environments:

### **Named Volumes for Production**
```yaml
# Production containers-compose.yml
volumes:
  - postgres_data:/var/lib/postgresql/data  # Named volume
  - redis_data:/data                        # Named volume
  - n8n_data:/home/node/.n8n               # Named volume

volumes:
  postgres_data:
  redis_data:
  n8n_data:
```

### **Why Named Volumes in Production?**
- **Performance**: Better performance in cloud environments
- **Management**: Docker handles volume lifecycle
- **Backup**: Integration with cloud backup solutions
- **Security**: No host filesystem exposure

## Troubleshooting

### **Permission Issues**
```bash
# Fix ownership (Linux/WSL2)
sudo chown -R $(id -u):$(id -g) infrastructure/volumes/

# Fix permissions
chmod -R 755 infrastructure/volumes/
```

### **Data Corruption**
```bash
# Check PostgreSQL logs
tail -f infrastructure/volumes/postgresql/data/log/postgresql-*.log

# Verify Redis integrity
podman exec sdlc-redis redis-cli --rdb-check-mode
```

### **Performance Issues on macOS**
```bash
# Alternative: Use named volumes for heavy workloads
# Edit containers-compose.yml to use named volumes temporarily
```

This approach provides the perfect balance for **local development**: transparency and control during development, with clear migration path to production-optimized volume management.
