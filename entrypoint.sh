#!/bin/bash
set -e

mkdir -p /tmp/clamav/logs /tmp/clamav/run /tmp/clamav/db

sed -i.bak \
    -e 's/^LocalSocket/#&/' \
    -e 's/^PidFile/#&/' \
    -e 's/^LogFile/#&/' \
    -e 's/^DatabaseDirectory/#&/' \
    -e 's/^TemporaryDirectory/#&/' \
    /etc/clamav/clamd.conf || true

cat >> /etc/clamav/clamd.conf <<EOF
DatabaseDirectory /tmp/clamav/db
TemporaryDirectory /tmp/clamav
LocalSocket /tmp/clamav/run/clamd.ctl
PidFile /tmp/clamav/run/clamd.pid
LogFile /tmp/clamav/logs/clamd.log
EOF

chmod -R 777 /tmp/clamav

echo "Updating virus database..."
freshclam --datadir=/tmp/clamav/db

echo "Starting freshclam daemon..."
freshclam --datadir=/tmp/clamav/db -d &

echo "Starting clamd..."
clamd &

echo "Waiting for ClamAV daemon to be ready..."
for i in $(seq 1 30); do
    if clamdscan --ping 1 2>/dev/null; then
        echo "ClamAV daemon is ready."
        break
    fi
    sleep 1
done

echo "Starting metrics server..."
python health.py &

echo "Starting scanner worker..."
exec python app.py
