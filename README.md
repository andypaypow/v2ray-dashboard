# V2Ray Dashboard

Dashboard web pour la gestion des appareils VLESS avec V2RayTun.

## 🎯 Fonctionnalités

- Gestion des appareils avec UUID unique
- Génération de liens VLESS pour V2RayTun
- Export JSON et Liens VLESS
- Gestion des dates d'expiration
- Instructions détaillées pour chaque appareil
- Statistiques en temps réel

## 📋 Prérequis

- Docker
- Xray ou V2Ray (support VLESS)
- Python 3.11+

## 🚀 Installation

### Sur le VPS

```bash
# Cloner le repo
git clone https://github.com/andypaypow/v2ray-dashboard.git
cd v2ray-dashboard

# Créer les dossiers
mkdir -p data public

# Copier les fichiers
cp server.py .
cp index.html public/

# Créer docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  v2ray-dashboard:
    image: python:3.11-slim
    container_name: v2ray-dashboard
    restart: unless-stopped
    working_dir: /app
    command: python3 -u server.py
    volumes:
      - ./public:/app/public
      - ./data:/app/data
      - ./server.py:/app/server.py
    ports:
      - "8094:8094"
EOF

# Démarrer
docker compose up -d
```

## 🔗 Configuration Xray/V2Ray

Le dashboard est configuré pour fonctionner avec Xray sur le port 8443 (VLESS).

Exemple de configuration Xray :

```json
{
  "inbounds": [
    {
      "port": 8443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "VOTRE_UUID",
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "none"
      }
    }
  ]
}
```

## 📱 Utilisation avec V2RayTun

1. Ouvrir le dashboard : http://VPS_IP:8094
2. Ajouter un appareil avec un nom
3. Cliquer sur "🔗 VLESS Link"
4. Copier le lien
5. Dans V2RayTun : Importer depuis le presse-papiers

## 🛠️ API

### GET /api/data
Retourne la configuration et les appareils.

### POST /api/save
Sauvegarde les appareils.

Body :
```json
{
  "devices": [...]
}
```

## 📊 Ports

| Service | Port |
|---------|------|
| Dashboard | 8094 |
| VLESS | 8443 |
| SOCKS5 | 1082 |
| HTTP | 1083 |

## 📝 Auteur

AndyPayPow

## 📄 Licence

MIT
