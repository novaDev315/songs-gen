# Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: "Command not found: songs-gen"

**Error Message**: `bash: songs-gen: command not found`

**Solution**:
```bash
# Install in development mode
pip install -e .

# Or run menu directly
python3 tools/menu.py
```

---

### Issue 2: "ModuleNotFoundError: No module named 'tools'"

**Error Message**: `ModuleNotFoundError: No module named 'tools'`

**Solution**:
```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/songs-gen"

# Or run from project root
cd /path/to/songs-gen
python3 tools/menu.py
```

---

### Issue 3: "Permission Denied" on menu.py

**Error Message**: `Permission denied: ./tools/menu.py`

**Solution**:
```bash
# Make menu.py executable
chmod +x tools/menu.py

# Or run with python3 explicitly
python3 tools/menu.py
```

---

### Issue 4: Songs not appearing in menu

**Problem**: Browse songs shows "No songs found"

**Solution**:
1. Verify songs exist in `generated/songs/` directory
2. Ensure song files end with `.md`
3. Regenerate indexes:
   ```bash
   python3 tools/management/index_manager.py --regenerate
   ```

---

### Issue 5: UUID collision warning

**Warning**: `UUID collision detected on attempt...`

**Note**: This is extremely rare and not usually a problem. The system automatically generates a new UUID.

**If it persists**:
1. Check system entropy: `cat /proc/sys/kernel/random/entropy_avail`
2. Restart services if on server
3. Report if collisions happen frequently

---

### Issue 6: "Encoding error" when reading song files

**Error**: `Encoding error in [filename]: ...`

**Solution**:
1. Ensure files are saved as UTF-8:
   ```bash
   file -i generated/songs/*/*.md
   ```
2. Convert if needed:
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 old-file.md > new-file.md
   ```

---

### Issue 7: Validation errors on all songs

**Problem**: All songs show validation errors

**Solution**:
1. Check if `generated/songs/` directory exists
2. Verify songs follow template structure:
   ```bash
   python3 tools/validation/validator.py --check-sample
   ```

---

## Platform-Specific Issues

### Windows

**Issue**: `.sh` scripts don't work

**Solution**: Use `.py` alternatives or use WSL (Windows Subsystem for Linux)

---

### macOS

**Issue**: "Command not recognized" on Big Sur+

**Solution**:
```bash
# Check Python version (need 3.8+)
python3 --version

# Update PATH if needed
export PATH="/usr/local/bin:$PATH"
```

---

### Linux

**Issue**: Permission denied on log directory

**Solution**:
```bash
# Create logs directory with proper permissions
mkdir -p logs
chmod 755 logs
```

---

## Performance Issues

### Slow song creation

**Cause**: UUID generation taking time on systems with low entropy

**Solution**:
```bash
# Check entropy
cat /proc/sys/kernel/random/entropy_avail

# On servers, consider using haveged
sudo apt-get install haveged
```

---

## Getting Help

1. **Check logs**: `cat logs/songs-gen-*.log`
2. **Enable debug logging**: Set environment variable
   ```bash
   export SONGS_GEN_LOG_LEVEL=DEBUG
   ```
3. **Report issues**: Include:
   - Error message
   - Python version: `python3 --version`
   - OS: `uname -a`
   - Log files

---

## Advanced Troubleshooting

### Enable debug logging
```bash
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from tools.menu import main
main()
"
```

### Test individual components
```bash
# Test UUID generator
python3 -c "from tools.core.uuid_generator import UUIDGenerator; print(UUIDGenerator().generate())"

# Test validator
python3 -c "from tools.validation.validator import validate_all_songs; from pathlib import Path; print(validate_all_songs(Path('.')))"
```

### Check system requirements
```bash
python3 -c "
import sys
print(f'Python: {sys.version}')
print(f'Platform: {sys.platform}')
print(f'Path: {sys.path}')
"
```
