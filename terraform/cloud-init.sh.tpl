#!/bin/bash
# Runs once on first VM boot (via Azure custom_data). Prepares the host so the
# Jenkins deploy stage only has to copy files and restart a service.
set -euxo pipefail

apt-get update -y
apt-get install -y python3 python3-venv python3-pip

mkdir -p /opt/webapp
chown -R azureuser:azureuser /opt/webapp

cat <<'EOF' > /etc/systemd/system/webapp.service
[Unit]
Description=CI/CD demo web application
After=network.target

[Service]
User=azureuser
WorkingDirectory=/opt/webapp
Environment="PATH=/opt/webapp/venv/bin"
ExecStart=/opt/webapp/venv/bin/gunicorn --bind 0.0.0.0:${app_port} app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable webapp.service
# Not started here - there is no app code on the VM yet. Jenkins' deploy stage
# copies the code, builds the venv, then starts/restarts this unit.
