#!/bin/bash
# Script de test avec cURL pour l'API Django 2FA Auth

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api/auth"

echo "🚀 Tests de l'API Django 2FA Auth avec cURL"
echo "=============================================="

# Variables pour stocker les tokens
ACCESS_TOKEN=""
REFRESH_TOKEN=""
SECRET_KEY=""

# Fonction pour afficher les réponses
print_response() {
    echo "📋 Réponse:"
    echo "$1" | jq '.' 2>/dev/null || echo "$1"
    echo ""
}

# Test 1: Inscription
echo "🧪 Test 1: Inscription d'un utilisateur"
echo "----------------------------------------"
REGISTRATION_RESPONSE=$(curl -s -X POST "$API_BASE/signup/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890",
    "language": "fr",
    "timezone": "Europe/Paris"
  }')

print_response "$REGISTRATION_RESPONSE"

# Extraire les tokens
ACCESS_TOKEN=$(echo "$REGISTRATION_RESPONSE" | jq -r '.tokens.access // empty')
REFRESH_TOKEN=$(echo "$REGISTRATION_RESPONSE" | jq -r '.tokens.refresh // empty')

if [ -n "$ACCESS_TOKEN" ]; then
    echo "✅ Inscription réussie! Token d'accès récupéré."
else
    echo "❌ Échec de l'inscription"
    exit 1
fi

# Test 2: Récupération du profil
echo "🧪 Test 2: Récupération du profil"
echo "----------------------------------"
PROFILE_RESPONSE=$(curl -s -X GET "$API_BASE/profile/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_response "$PROFILE_RESPONSE"

# Test 3: Mise à jour du profil
echo "🧪 Test 3: Mise à jour du profil"
echo "---------------------------------"
UPDATE_RESPONSE=$(curl -s -X PUT "$API_BASE/profile/update/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test Updated",
    "language": "en",
    "timezone": "America/New_York"
  }')

print_response "$UPDATE_RESPONSE"

# Test 4: Configuration 2FA
echo "🧪 Test 4: Configuration 2FA"
echo "-----------------------------"
TWOFA_SETUP_RESPONSE=$(curl -s -X POST "$API_BASE/2fa/setup/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_response "$TWOFA_SETUP_RESPONSE"

# Extraire la clé secrète
SECRET_KEY=$(echo "$TWOFA_SETUP_RESPONSE" | jq -r '.setup_data.secret_key // empty')

if [ -n "$SECRET_KEY" ]; then
    echo "✅ Configuration 2FA générée! Secret key: $SECRET_KEY"
else
    echo "❌ Échec de la configuration 2FA"
fi

# Test 5: Statut 2FA
echo "🧪 Test 5: Statut 2FA"
echo "----------------------"
STATUS_RESPONSE=$(curl -s -X GET "$API_BASE/2fa/status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

print_response "$STATUS_RESPONSE"

# Test 6: Rafraîchissement des tokens
echo "🧪 Test 6: Rafraîchissement des tokens"
echo "---------------------------------------"
REFRESH_RESPONSE=$(curl -s -X POST "$API_BASE/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}")

print_response "$REFRESH_RESPONSE"

# Extraire le nouveau token d'accès
NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access // empty')

if [ -n "$NEW_ACCESS_TOKEN" ]; then
    echo "✅ Tokens rafraîchis! Nouveau token d'accès récupéré."
    ACCESS_TOKEN="$NEW_ACCESS_TOKEN"
else
    echo "❌ Échec du rafraîchissement des tokens"
fi

# Test 7: Connexion
echo "🧪 Test 7: Connexion utilisateur"
echo "---------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/signin/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }')

print_response "$LOGIN_RESPONSE"

# Test 8: Déconnexion
echo "🧪 Test 8: Déconnexion"
echo "-----------------------"
LOGOUT_RESPONSE=$(curl -s -X POST "$API_BASE/logout/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

print_response "$LOGOUT_RESPONSE"

echo "🏁 Tests terminés!"
echo "=================="
echo "📝 Note: Pour tester la vérification 2FA, vous devez:"
echo "   1. Utiliser une application d'authentification (Google Authenticator, Authy)"
echo "   2. Scanner le QR code généré lors de la configuration 2FA"
echo "   3. Utiliser le code TOTP généré pour vérifier l'activation"
echo "   4. Tester la connexion avec 2FA activé"



