# Naveen Kumar Electrical Works

Dharmapuri vehicle electrical shop site (GM Theatre backside).
Tamil + English. WhatsApp + lead form + admin.

Repo: https://github.com/rajkumar-madhu/naveen-kumar-electrical-works

## Run locally

```bash
python3 -m pip install -r requirements.txt
mkdir -p frontend/assets data
# copy flyer.png into frontend/assets/
ADMIN_TOKEN=naveen-admin-2026 python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

- Site: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

## Docker

```bash
docker compose up --build -d
```

## Hostinger VPS

```bash
git clone https://github.com/rajkumar-madhu/naveen-kumar-electrical-works.git
cd naveen-kumar-electrical-works
cp .env.example .env   # set a strong ADMIN_TOKEN
mkdir -p frontend/assets data
# copy flyer.png into frontend/assets/
docker compose up --build -d
```

Point Nginx to `127.0.0.1:8000` using `deploy/nginx.conf`, then Certbot HTTPS.

## Contact

Naveen Kumar · +91 80986 73590 · GM Theatre Back Side, Dharmapuri 636701
