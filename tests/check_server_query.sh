#!/bin/bash
# Check if production server has the correct OUTER APPLY query

echo "=========================================="
echo "CHECKING PRODUCTION SERVER QUERY"
echo "=========================================="

# Navigate to project directory
cd ~/Inspection-System

# Check if data_views.py has OUTER APPLY
echo -e "\n1. Checking if OUTER APPLY is in data_views.py..."
grep -c "OUTER APPLY" main/views/data_views.py

if grep -q "OUTER APPLY" main/views/data_views.py; then
    echo "   ✅ OUTER APPLY found in source file"
else
    echo "   ❌ OUTER APPLY NOT found in source file!"
fi

# Clear Python bytecode cache
echo -e "\n2. Clearing Python bytecode cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo "   ✅ Bytecode cache cleared"

# Restart Gunicorn to reload code
echo -e "\n3. Restarting Gunicorn to reload code..."
sudo systemctl restart gunicorn
sleep 3
echo "   ✅ Gunicorn restarted"

# Check Gunicorn status
echo -e "\n4. Checking Gunicorn status..."
sudo systemctl status gunicorn --no-pager | grep -E "(Active|Main PID)"

echo -e "\n=========================================="
echo "DONE - Server should now use OUTER APPLY"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to the web interface"
echo "2. Click 'Sync Everything' button"
echo "3. Check if inspection count stays around 3.1k-3.7k"
echo ""
