#!/bin/bash
# BMOS�����ڲ��Խű�

echo "=== BMOS�����ڲ��� ==="

echo "1. ����ClickHouse����:"
clickhouse-client --query "SELECT 1"

echo "2. �������ݿ�:"
clickhouse-client --query "SHOW DATABASES"

echo "3. ����BMOS��:"
clickhouse-client --query "SHOW TABLES FROM bmos"

echo "4. ����HTTP�ӿ�:"
curl -s "http://localhost:8123/?query=SELECT%201"

echo "5. ����Redis����:"
nc -z localhost 6379 && echo "Redis��������" || echo "Redis����ʧ��"

echo "=== ������� ==="
