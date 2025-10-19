#!/bin/bash
# BMOS容器内测试脚本

echo "=== BMOS容器内测试 ==="

echo "1. 测试ClickHouse连接:"
clickhouse-client --query "SELECT 1"

echo "2. 测试数据库:"
clickhouse-client --query "SHOW DATABASES"

echo "3. 测试BMOS表:"
clickhouse-client --query "SHOW TABLES FROM bmos"

echo "4. 测试HTTP接口:"
curl -s "http://localhost:8123/?query=SELECT%201"

echo "5. 测试Redis连接:"
nc -z localhost 6379 && echo "Redis连接正常" || echo "Redis连接失败"

echo "=== 测试完成 ==="
