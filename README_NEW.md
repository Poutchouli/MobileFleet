# 📱 MobileFleet - Système de Gestion de Flotte Mobile

Application web complète pour la gestion d'une flotte de téléphones mobiles d'entreprise.

## 🚀 Fonctionnalités Principales

### 👥 Gestion Multi-Rôles
- **Administrateurs** : Vue d'ensemble complète, gestion des utilisateurs et configuration
- **Managers** : Gestion des tickets pour leur secteur, suivi des équipements
- **Support Technique** : Résolution des tickets, gestion des échanges d'équipements

### 🎫 Système de Tickets
- Création et suivi de tickets pour problèmes d'équipements
- Interface complètement traduite en français
- Gestion des commentaires et mises à jour
- Workflow de résolution avec historique complet

### 📊 Vue d'Ensemble Admin
- Cartes interactives des travailleurs avec édition en ligne
- Filtrage avancé par secteur, statut, type de contrat
- Alertes visuelles pour les contrats CDD expirant
- Statistiques en temps réel (tickets, historique téléphones)

### 🔧 Gestion des Données
- Intégration système Philia (ID/MDP)
- Suivi complet des assignments de téléphones
- Gestion des contrats et alertes d'expiration
- Base de données PostgreSQL robuste

## 🛠️ Architecture Technique

### Stack Technologique
- **Backend** : Python Flask avec Gunicorn
- **Base de Données** : PostgreSQL
- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **Containerisation** : Docker & Docker Compose
- **Styles** : Framework CSS personnalisé avec Tailwind-like classes

### Structure du Projet
```
MobileFleet/
├── main.py                 # Application Flask principale
├── init_database.py        # Initialisation et setup de la BDD
├── requirements.txt        # Dépendances Python
├── Dockerfile             # Configuration Docker
├── docker-compose.yml     # Orchestration des services
├── static/                # Fichiers statiques (CSS, JS)
├── templates/             # Templates Jinja2
├── migrations/            # Scripts de migration BDD
├── logs/                  # Fichiers de logs
└── OLD_STUFF/            # Fichiers archivés
```

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose installés
- Git pour cloner le repository

### Installation et Lancement
```bash
# Cloner le repository
git clone [repository-url]
cd MobileFleet

# Lancer l'application avec Docker
docker-compose up --build

# L'application sera accessible sur http://localhost:5000
```

### Comptes de Test
- **Admin** : `admin` / `password`
- **Manager Nord** : `manager_north` / `password`
- **Manager Sud** : `manager_south` / `password`
- **Support** : `support_user` / `password`

## 🗃️ Base de Données

La base de données est automatiquement initialisée au premier démarrage avec :
- Structure complète des tables
- Données d'exemple pour les tests
- Utilisateurs de démonstration
- Secteurs et équipements de base

### Tables Principales
- `users` - Utilisateurs et authentification
- `workers` - Employés de l'entreprise
- `rh_data` - Données RH (contrats, Philia)
- `phones` - Équipements mobiles
- `tickets` - Système de tickets
- `assignments` - Historique des attributions

## 🔧 Configuration

### Variables d'Environnement
Le fichier `.env` contient la configuration de l'application :
```env
DATABASE_URL=postgresql://postgres:password@db:5432/fleet_db
FLASK_ENV=development
SECRET_KEY=[clé-secrete]
```

### Mode Développement vs Production
- **Développement** : Base de données réinitialisée à chaque démarrage
- **Production** : Conservation des données existantes

## 🎨 Interface Utilisateur

### Responsive Design
- Interface adaptée mobile, tablette et desktop
- Navigation intuitive avec sidebar contextuelle
- Thème moderne avec alertes visuelles

### Fonctionnalités UX
- Pagination intelligente
- Filtres en temps réel
- Édition en ligne avec validation
- Messages toast pour les confirmations
- Alertes automatiques pour les contrats

## 📈 Évolutions Récentes

### Version Actuelle (Juillet 2025)
✅ **Complété :**
- Traduction complète en français
- Système de tickets fonctionnel
- Vue d'ensemble admin avec édition
- APIs complètes pour la gestion
- Intégration des données Philia
- Statistiques et alertes

### Fonctionnalités Clés
- **Correction du bug de création de tickets** : Validation JavaScript corrigée
- **Interface admin avancée** : Cartes interactives avec édition en ligne
- **Nouvelles APIs** : `/api/sectors` et `/api/admin/worker/<id>`
- **Statistiques enrichies** : Total tickets et historique téléphones
- **Alertes contrats** : Notifications visuelles pour CDD expirants

## 🤝 Contribution

Le code est structuré pour faciliter les évolutions futures :
- Architecture modulaire
- APIs RESTful bien définies
- Templates réutilisables
- Documentation complète

## 📞 Support

Pour toute question technique, consulter :
- Les logs de l'application dans `logs/`
- La documentation archivée dans `OLD_STUFF/`
- Les commentaires dans le code source

---

**MobileFleet** - Solution complète de gestion de flotte mobile d'entreprise
*Développé avec ❤️ en Python Flask*
