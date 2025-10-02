#!/bin/bash

# Linux System Performance Optimization Script
# Run with: sudo bash optimize_system.sh

echo "=== Linux System Performance Optimization ==="
echo "Starting optimization process..."

# 1. CPU Performance Optimization
echo "1. Optimizing CPU performance..."
# Set CPU governor to performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $cpu > /dev/null 2>&1
done

# Enable CPU boost if available
echo 1 | sudo tee /sys/devices/system/cpu/cpufreq/boost > /dev/null 2>&1

# 2. Memory Optimization
echo "2. Optimizing memory settings..."
# Increase dirty ratio for better write performance
echo 15 | sudo tee /proc/sys/vm/dirty_ratio > /dev/null
echo 5 | sudo tee /proc/sys/vm/dirty_background_ratio > /dev/null

# Optimize swap usage
echo 10 | sudo tee /proc/sys/vm/swappiness > /dev/null

# Enable transparent huge pages for better memory management
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null 2>&1

# 3. I/O Scheduler Optimization
echo "3. Optimizing I/O scheduler..."
# Set mq-deadline for SSDs (already set, but ensure it's optimal)
for disk in /sys/block/sd*/queue/scheduler; do
    if [ -f "$disk" ]; then
        echo mq-deadline | sudo tee $disk > /dev/null 2>&1
    fi
done

# Increase read-ahead for better sequential read performance
for disk in /sys/block/sd*/queue/read_ahead_kb; do
    if [ -f "$disk" ]; then
        echo 1024 | sudo tee $disk > /dev/null 2>&1
    fi
done

# 4. Network Optimization
echo "4. Optimizing network settings..."
# Increase network buffer sizes
echo 16777216 | sudo tee /proc/sys/net/core/rmem_max > /dev/null
echo 16777216 | sudo tee /proc/sys/net/core/wmem_max > /dev/null
echo 262144 | sudo tee /proc/sys/net/core/rmem_default > /dev/null
echo 262144 | sudo tee /proc/sys/net/core/wmem_default > /dev/null

# Optimize TCP settings
echo 1 | sudo tee /proc/sys/net/ipv4/tcp_window_scaling > /dev/null
echo 1 | sudo tee /proc/sys/net/ipv4/tcp_timestamps > /dev/null
echo 1 | sudo tee /proc/sys/net/ipv4/tcp_sack > /dev/null

# 5. Kernel Parameter Optimization
echo "5. Optimizing kernel parameters..."
# Increase file descriptor limits
echo 65536 | sudo tee /proc/sys/fs/file-max > /dev/null
echo 65536 | sudo tee /proc/sys/fs/inotify/max_user_watches > /dev/null

# Optimize process limits
echo 32768 | sudo tee /proc/sys/kernel/pid_max > /dev/null

# 6. Disable unnecessary services (optional - be careful)
echo "6. Checking for unnecessary services..."
# List services that can be disabled for better performance
echo "Services that can be disabled for better performance:"
echo "- cups.service (if no printing needed)"
echo "- bluetooth.service (if not using Bluetooth)"
echo "- ModemManager.service (if not using mobile broadband)"

# 7. Clear caches and optimize memory
echo "7. Clearing caches..."
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

# 8. Set up performance monitoring
echo "8. Setting up performance monitoring..."
# Create a simple performance monitoring script
cat > /tmp/performance_monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Performance Monitor ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
echo "Memory Usage:"
free -h | grep "Mem:" | awk '{print "Used: " $3 " / " $2 " (" $3/$2*100 "%)"}'
echo "Load Average:"
uptime | awk -F'load average:' '{print $2}'
echo "Disk I/O:"
iostat -x 1 1 2>/dev/null | tail -n +4 | head -n -1
EOF

chmod +x /tmp/performance_monitor.sh

echo "=== Optimization Complete ==="
echo "Current CPU Governor:"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo "Current Memory Settings:"
echo "Dirty ratio: $(cat /proc/sys/vm/dirty_ratio)"
echo "Swappiness: $(cat /proc/sys/vm/swappiness)"
echo "Current I/O Scheduler:"
cat /sys/block/sda/queue/scheduler 2>/dev/null || echo "N/A"

echo ""
echo "To monitor performance, run: /tmp/performance_monitor.sh"
echo "To make changes permanent, add the following to /etc/sysctl.conf:"
echo "vm.dirty_ratio = 15"
echo "vm.dirty_background_ratio = 5"
echo "vm.swappiness = 10"
echo "net.core.rmem_max = 16777216"
echo "net.core.wmem_max = 16777216"
echo "net.core.rmem_default = 262144"
echo "net.core.wmem_default = 262144"
echo "net.ipv4.tcp_window_scaling = 1"
echo "net.ipv4.tcp_timestamps = 1"
echo "net.ipv4.tcp_sack = 1"
echo "fs.file-max = 65536"
echo "fs.inotify.max_user_watches = 65536"
echo "kernel.pid_max = 32768"
