#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y docker awscli

systemctl enable docker
systemctl start docker

usermod -aG docker ec2-user

ACCOUNT_ID=$(echo "${docker_image}" | cut -d'.' -f1)
REGISTRY="$ACCOUNT_ID.dkr.ecr.${aws_region}.amazonaws.com"

aws ecr get-login-password --region "${aws_region}" \
  | docker login --username AWS --password-stdin "$REGISTRY"

docker pull "${docker_image}"
docker rm -f "${app_name}" || true

docker run -d \
  --name "${app_name}" \
  --restart unless-stopped \
  -p 80:${app_port} \
  -e FLASK_ENV=production \
  -e SECRET_KEY='${secret_key}' \
  -e DB_HOST='${db_host}' \
  -e DB_NAME='${db_name}' \
  -e DB_USER='${db_user}' \
  -e DB_PASSWORD='${db_password}' \
  "${docker_image}"