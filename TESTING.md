# 🧪 Guide de Test de l'API Django 2FA Auth

Ce guide vous explique comment tester l'API d'authentification avec 2FA.

## 📋 Fichiers de Test Disponibles

| Fichier | Description | Utilisation |
|---------|-------------|-------------|
| `test_quick.py` | Test rapide des endpoints principaux | `python test_quick.py` |
| `test_api_complete.py` | Tests complets avec 2FA | `python test_api_complete.py` |
| `test_curl_commands.sh` | Tests avec cURL (Linux/Mac) | `./test_curl_commands.sh` |
| `API_EXAMPLES.md` | Exemples de payloads détaillés | Documentation |

## 🚀 Démarrage Rapide

### 1. Démarrer le Serveur

```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1  # Windows
# ou
source venv/bin/activate     # Linux/Mac

# Démarrer le serveur Django
python manage.py runserver
```

### 2. Test Rapide

```bash
python test_quick.py
```

### 3. Tests Complets

```bash
python test_api_complete.py
```

## 🔧 Prérequis

### Python
- Python 3.9+
- Environnement virtuel activé
- Dépendances installées (`pip install -r requirements/base.txt`)

### Packages Python pour les Tests
```bash
pip install requests pyotp
```

### Outils Optionnels
- **cURL** : Pour les tests en ligne de commande
- **jq** : Pour formater les réponses JSON
- **Postman** : Interface graphique pour les tests

## 📱 Test de la 2FA

### 1. Configuration 2FA

1. Exécutez le test de configuration 2FA
2. Récupérez le QR code généré
3. Scannez le QR code avec une app d'authentification :
   - **Google Authenticator**
   - **Authy**
   - **Microsoft Authenticator**

### 2. Vérification 2FA

1. Utilisez le code TOTP généré par l'app
2. Ou utilisez un code de secours fourni
3. Testez la connexion avec 2FA activé

## 🧪 Exemples de Tests

### Test d'Inscription

```python
import requests

response = requests.post("http://localhost:8000/api/auth/signup/", json={
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
})

print(response.json())
```

### Test de Connexion

```python
response = requests.post("http://localhost:8000/api/auth/signin/", json={
    "email": "test@example.com",
    "password": "TestPassword123!"
})

print(response.json())
```

### Test avec Token

```python
headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
response = requests.get("http://localhost:8000/api/auth/profile/", headers=headers)
print(response.json())
```

## 🔍 Dépannage

### Erreur de Connexion
- Vérifiez que le serveur Django est démarré
- Vérifiez l'URL (http://localhost:8000)
- Vérifiez que l'environnement virtuel est activé

### Erreur d'Import
```bash
pip install requests pyotp
```

### Erreur de Token
- Vérifiez que l'utilisateur est bien créé
- Vérifiez que la connexion a réussi
- Vérifiez le format du token (Bearer + espace + token)

### Erreur 2FA
- Vérifiez que la 2FA est bien configurée
- Vérifiez que le code TOTP est valide (30 secondes)
- Vérifiez que l'application d'authentification est synchronisée

## 📊 Endpoints Testés

### ✅ Authentification de Base
- [x] POST `/api/auth/signup/` - Inscription
- [x] POST `/api/auth/signin/` - Connexion
- [x] POST `/api/auth/logout/` - Déconnexion
- [x] POST `/api/auth/token/refresh/` - Rafraîchissement tokens

### ✅ Gestion du Profil
- [x] GET `/api/auth/profile/` - Récupération profil
- [x] PUT `/api/auth/profile/update/` - Mise à jour profil

### ✅ Authentification 2FA
- [x] POST `/api/auth/2fa/setup/` - Configuration 2FA
- [x] POST `/api/auth/2fa/verify-setup/` - Vérification 2FA
- [x] POST `/api/auth/2fa/verify-login/` - Connexion avec 2FA
- [x] GET `/api/auth/2fa/status/` - Statut 2FA
- [x] POST `/api/auth/2fa/regenerate-backup-codes/` - Codes de secours
- [x] POST `/api/auth/2fa/disable/` - Désactivation 2FA

## 🎯 Workflow de Test Complet

1. **Inscription** → Créer un utilisateur
2. **Connexion** → Authentifier l'utilisateur
3. **Profil** → Tester l'accès protégé
4. **Configuration 2FA** → Générer QR code
5. **Activation 2FA** → Vérifier avec code TOTP
6. **Connexion 2FA** → Tester le workflow complet
7. **Statut 2FA** → Vérifier l'état
8. **Déconnexion** → Nettoyer les sessions

## 📝 Logs et Debug

### Activer les Logs Django
```python
# Dans settings/development.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Vérifier la Base de Données
```bash
python manage.py shell
>>> from apps.authentication.models import User
>>> User.objects.all()
>>> User.objects.get(email='test@example.com')
```

## 🚨 Codes d'Erreur Courants

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Vérifier le format des données |
| 401 | Unauthorized | Vérifier le token d'accès |
| 403 | Forbidden | Vérifier les permissions |
| 404 | Not Found | Vérifier l'URL de l'endpoint |
| 429 | Too Many Requests | Attendre ou vérifier le rate limiting |
| 500 | Internal Server Error | Vérifier les logs Django |

---

**🎉 Bon test de l'API !**



