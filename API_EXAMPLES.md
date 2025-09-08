# 🧪 Exemples de Payloads pour l'API Django 2FA Auth

Ce fichier contient tous les exemples de requêtes pour tester l'API d'authentification avec 2FA.

## 📋 Table des Matières

- [🔐 Authentification de Base](#-authentification-de-base)
- [👤 Gestion du Profil](#-gestion-du-profil)
- [🔑 Authentification 2FA](#-authentification-2fa)
- [🧪 Tests avec cURL](#-tests-avec-curl)
- [📱 Tests avec Postman](#-tests-avec-postman)
## 🔐 Authentification de Base

### 1. Inscription d'un Utilisateur

**Endpoint:** `POST /api/auth/signup/`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "language": "fr",
  "timezone": "Europe/Paris"
}
```

**Réponse attendue (201):**
```json
{
  "message": "Compte créé avec succès. Bienvenue !",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "avatar": null,
    "is_verified": false,
    "two_factor_enabled": false,
    "language": "fr",
    "timezone": "Europe/Paris",
    "email_notifications": true,
    "created_at": "2024-01-01T12:00:00Z",
    "last_activity": null
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 2. Connexion Utilisateur

**Endpoint:** `POST /api/auth/signin/`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!"
}
```

**Réponse attendue (200):**
```json
{
  "message": "Connexion réussie.",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "two_factor_enabled": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "requires_2fa": false
}
```

### 3. Rafraîchissement des Tokens

**Endpoint:** `POST /api/auth/token/refresh/`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse attendue (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Déconnexion

**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse attendue (200):**
```json
{
  "message": "Déconnexion réussie."
}
```

---

## 👤 Gestion du Profil

### 1. Récupérer le Profil

**Endpoint:** `GET /api/auth/profile/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse attendue (200):**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "avatar": null,
  "is_verified": false,
  "two_factor_enabled": false,
  "language": "fr",
  "timezone": "Europe/Paris",
  "email_notifications": true,
  "created_at": "2024-01-01T12:00:00Z",
  "last_activity": "2024-01-01T12:30:00Z"
}
```

### 2. Mettre à Jour le Profil

**Endpoint:** `PUT /api/auth/profile/update/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+0987654321",
  "language": "en",
  "timezone": "America/New_York",
  "email_notifications": false
}
```

**Réponse attendue (200):**
```json
{
  "message": "Profil mis à jour avec succès.",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+0987654321",
    "language": "en",
    "timezone": "America/New_York",
    "email_notifications": false
  }
}
```

---

## 🔑 Authentification 2FA

### 1. Configuration 2FA

**Endpoint:** `POST /api/auth/2fa/setup/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse attendue (200):**
```json
{
  "message": "Configuration 2FA générée. Scannez le QR code avec votre application d'authentification.",
  "setup_data": {
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "secret_key": "JBSWY3DPEHPK3PXP",
    "backup_codes": [
      "12345678",
      "87654321",
      "11223344",
      "55667788",
      "99887766"
    ],
    "totp_uri": "otpauth://totp/john.doe@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Django%202FA%20Auth%20API"
  }
}
```

### 2. Vérification et Activation 2FA

**Endpoint:** `POST /api/auth/2fa/verify-setup/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "Content-Type": "application/json"
}
```

**Payload (Code TOTP):**
```json
{
  "code": "123456"
}
```

**Payload (Code de Secours):**
```json
{
  "code": "12345678"
}
```

**Réponse attendue (200):**
```json
{
  "message": "Authentification à deux facteurs activée avec succès.",
  "verification_method": "totp"
}
```

### 3. Vérification 2FA lors de la Connexion

**Endpoint:** `POST /api/auth/2fa/verify-login/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "code": "123456"
}
```

**Réponse attendue (200):**
```json
{
  "message": "Connexion réussie avec authentification à deux facteurs.",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "two_factor_enabled": true
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "verification_method": "totp"
}
```

### 4. Statut de la 2FA

**Endpoint:** `GET /api/auth/2fa/status/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse attendue (200):**
```json
{
  "is_enabled": true,
  "is_configured": true,
  "backup_codes_count": 4,
  "last_used": "2024-01-01T12:30:00Z"
}
```

### 5. Régénération des Codes de Secours

**Endpoint:** `POST /api/auth/2fa/regenerate-backup-codes/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse attendue (200):**
```json
{
  "message": "Codes de secours régénérés avec succès.",
  "backup_codes": [
    "ABCD1234",
    "EFGH5678",
    "IJKL9012",
    "MNOP3456",
    "QRST7890"
  ]
}
```

### 6. Désactivation 2FA

**Endpoint:** `POST /api/auth/2fa/disable/`

**Headers:**
```json
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "Content-Type": "application/json"
}
```

**Payload:**
```json
{
  "password": "SecurePassword123!"
}
```

**Réponse attendue (200):**
```json
{
  "message": "Authentification à deux facteurs désactivée avec succès."
}
```

---

## 🧪 Tests avec cURL

### 1. Inscription
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Connexion
```bash
curl -X POST http://localhost:8000/api/auth/signin/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### 3. Profil (avec token)
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Configuration 2FA
```bash
curl -X POST http://localhost:8000/api/auth/2fa/setup/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📱 Tests avec Postman

### Collection Postman

Créez une collection Postman avec les requêtes suivantes :

1. **Inscription** - POST `{{base_url}}/api/auth/signup/`
2. **Connexion** - POST `{{base_url}}/api/auth/signin/`
3. **Profil** - GET `{{base_url}}/api/auth/profile/`
4. **Mise à jour Profil** - PUT `{{base_url}}/api/auth/profile/update/`
5. **Configuration 2FA** - POST `{{base_url}}/api/auth/2fa/setup/`
6. **Vérification 2FA** - POST `{{base_url}}/api/auth/2fa/verify-setup/`
7. **Statut 2FA** - GET `{{base_url}}/api/auth/2fa/status/`
8. **Déconnexion** - POST `{{base_url}}/api/auth/logout/`

### Variables d'Environnement Postman

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "refresh_token": "",
  "user_email": "test@example.com",
  "user_password": "TestPassword123!"
}
```

### Scripts Postman

**Script de test automatique (Tests tab):**
```javascript
// Sauvegarder le token d'accès
if (pm.response.code === 200 || pm.response.code === 201) {
    const responseJson = pm.response.json();
    if (responseJson.tokens) {
        pm.environment.set("access_token", responseJson.tokens.access);
        pm.environment.set("refresh_token", responseJson.tokens.refresh);
    }
}

// Vérifier la réponse
pm.test("Status code is 200 or 201", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});

pm.test("Response has message", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('message');
});
```

---

## 🚨 Codes d'Erreur Courants

### 400 - Bad Request
```json
{
  "email": ["Un utilisateur avec cet email existe déjà."],
  "password": ["Ce mot de passe est trop court."],
  "confirm_password": ["Les mots de passe ne correspondent pas."]
}
```

### 401 - Unauthorized
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### 403 - Forbidden
```json
{
  "error": "L'authentification à deux facteurs n'est pas activée."
}
```

### 429 - Too Many Requests
```json
{
  "error": "Votre compte est temporairement verrouillé. Veuillez réessayer plus tard."
}
```

---

## 🎯 Workflow de Test Complet

1. **Inscription** → Récupérer les tokens
2. **Connexion** → Vérifier l'authentification
3. **Profil** → Tester l'accès protégé
4. **Configuration 2FA** → Générer QR code
5. **Vérification 2FA** → Activer avec code TOTP
6. **Connexion avec 2FA** → Tester le workflow complet
7. **Statut 2FA** → Vérifier l'état
8. **Déconnexion** → Nettoyer les sessions

---

**🎉 Bon test de l'API !**

