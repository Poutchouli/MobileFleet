# Docker Compose Configurations

Ce projet dispose de deux configurations Docker Compose pour différents environnements :

## 📋 Configurations Disponibles

### 1. **Development** (`docker-compose.yml`)
- **Usage** : Développement et tests
- **Base de données** : ⚠️ **ÉCRASE** la base de données à chaque démarrage
- **Initialisation** : Exécute automatiquement `init_database.py`
- **Port** : 5000 (web), 5433 (PostgreSQL)
- **Volume** : `postgres_data`

### 2. **Production** (`docker-compose.prod.yml`)
- **Usage** : Production et environnements existants
- **Base de données** : ✅ **PRÉSERVE** la base de données existante
- **Initialisation** : Évite l'exécution de `init_database.py`
- **Port** : 5000 (web), 5434 (PostgreSQL)
- **Volume** : `postgres_data_prod`
- **Workers** : 4 workers Gunicorn pour les performances

## 🚀 Commandes d'Utilisation

### Développement (écrase la DB)
```bash
# Démarrer en mode développement
docker-compose up --build

# Arrêter et supprimer les conteneurs
docker-compose down

# Supprimer aussi les volumes (reset complet)
docker-compose down -v
```

### Production (préserve la DB)
```bash
# Démarrer en mode production
docker-compose -f docker-compose.prod.yml up --build

# Arrêter
docker-compose -f docker-compose.prod.yml down

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔧 Variables d'Environnement

### Development
- `FLASK_ENV=development`
- `FLASK_DEBUG=True` (par défaut)

### Production
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`

## 📊 Différences Techniques

| Aspect | Development | Production |
|--------|-------------|------------|
| Script d'init | ✅ Exécuté | ❌ Ignoré |
| Code mounting | ✅ Volume live | ❌ Code dans l'image |
| Workers | 2 | 4 |
| Restart policy | Non | `unless-stopped` |
| Port DB | 5433 | 5434 |
| Volume DB | `postgres_data` | `postgres_data_prod` |

## ⚠️ Avertissements

1. **Ne jamais utiliser la config development en production** - vous perdriez toutes vos données !
2. **La config production nécessite une DB existante** - initialisez d'abord avec la config development si nécessaire
3. **Vérifiez les ports** - les deux configs utilisent des ports différents pour éviter les conflits

## 🔄 Migration Development → Production

1. Développez avec `docker-compose.yml`
2. Une fois satisfait, arrêtez : `docker-compose down`
3. Basculez vers prod : `docker-compose -f docker-compose.prod.yml up --build`
4. Vos données seront préservées dans le volume `postgres_data_prod`
