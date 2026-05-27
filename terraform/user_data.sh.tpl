#!/bin/bash
set -euxo pipefail

# 1. Update and install Docker & Git
dnf update -y
dnf install -y docker awscli git

# Start Docker
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# 2. Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Create app directory and set up files
mkdir -p /app/nginx
cd /app

# Download your docker-compose and nginx files directly from your GitHub repo!
# (הערה: שנה את "YaakovNeriya" ליוזר האמיתי שלך בגיטהאב אם זה שונה)
curl -o docker-compose.yml https://raw.githubusercontent.com/YaakovNeriya/CashFlow/main/docker-compose.yml
curl -o nginx/nginx.conf https://raw.githubusercontent.com/YaakovNeriya/CashFlow/main/nginx/nginx.conf

# 4. Create the secure .env file dynamically from Terraform variables
cat <<EOF > .env
DB_HOST=mysql
DB_USER=${db_user}
DB_PASSWORD=${db_password}
DB_NAME=${db_name}
SECRET_KEY=${secret_key}
FLASK_DEBUG=false
APP_IMAGE=${docker_image}
EOF

# 5. Login to AWS ECR and pull your custom image
ACCOUNT_ID=$(echo "${docker_image}" | cut -d'.' -f1)
REGISTRY="$ACCOUNT_ID.dkr.ecr.${aws_region}.amazonaws.com"
aws ecr get-login-password --region "${aws_region}" | docker login --username AWS --password-stdin "$REGISTRY"

docker pull "${docker_image}"

# 6. Start the whole stack (Flask + MySQL + Nginx)
docker-compose up -d
