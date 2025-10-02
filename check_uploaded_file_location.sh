#!/bin/bash
# Check where the uploaded file actually went

echo "=== Checking for recently uploaded RFI file ==="
echo ""

# Find the file that was just uploaded
echo "Looking for: Eggbert_Eggs_Pty_Ltd_Arendnes_20250926_rfi_20251001_142026.pdf"
echo ""

# Search in the inspection folder
find /root/Inspection-System/media/inspection -name "*Eggbert*" -type f 2>/dev/null

echo ""
echo "=== Checking folder structure in /media/inspection/2025/ ==="
ls -la /root/Inspection-System/media/inspection/2025/ 2>/dev/null

echo ""
echo "=== If September folder exists, show its contents ==="
ls -la /root/Inspection-System/media/inspection/2025/September/ 2>/dev/null

echo ""
echo "=== Search for any files uploaded today ==="
find /root/Inspection-System/media/inspection -type f -newermt "2025-10-01" 2>/dev/null

echo ""
echo "=== Show full directory tree (first 50 lines) ==="
find /root/Inspection-System/media/inspection -type d 2>/dev/null | head -50

