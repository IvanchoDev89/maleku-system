#!/bin/bash
echo "=== Checking ports ==="
netstat -tlnp 2>/dev/null | grep -E ':(3000|8000|45975)' || ss -tlnp 2>/dev/null | grep -E ':(3000|8000|45975)'
echo ""
echo "=== Checking Nuxt processes ==="
ps aux | grep -E "nuxt|node.*vue|node.*nuxt" | grep -v grep
echo ""
echo "=== Done ==="
