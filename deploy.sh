SECRET_KEY="$(openssl rand -hex 32)" \
PUBLIC_API_PORT=8000 \
docker compose up --build