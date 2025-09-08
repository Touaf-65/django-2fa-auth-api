"""
Messages constants for the Core application
"""
SUCCESS_MESSAGES = {
    'USER_CREATED': 'Utilisateur créé avec succès',
    'USER_UPDATED': 'Utilisateur mis à jour avec succès',
    'USER_DELETED': 'Utilisateur supprimé avec succès',
    'PASSWORD_CHANGED': 'Mot de passe modifié avec succès',
    'EMAIL_SENT': 'Email envoyé avec succès',
    'NOTIFICATION_SENT': 'Notification envoyée avec succès',
    'PERMISSION_GRANTED': 'Permission accordée avec succès',
    'ROLE_ASSIGNED': 'Rôle attribué avec succès',
    'GROUP_CREATED': 'Groupe créé avec succès',
}

ERROR_MESSAGES = {
    'INVALID_CREDENTIALS': 'Identifiants invalides',
    'USER_NOT_FOUND': 'Utilisateur non trouvé',
    'PERMISSION_DENIED': 'Permission refusée',
    'VALIDATION_ERROR': 'Erreur de validation',
    'INTERNAL_ERROR': 'Erreur interne du serveur',
    'RATE_LIMIT_EXCEEDED': 'Limite de taux dépassée',
    'INVALID_TOKEN': 'Token invalide',
    'TOKEN_EXPIRED': 'Token expiré',
}

WARNING_MESSAGES = {
    'WEAK_PASSWORD': 'Mot de passe faible détecté',
    'SUSPICIOUS_ACTIVITY': 'Activité suspecte détectée',
    'LOGIN_ATTEMPT_LIMIT': 'Limite de tentatives de connexion atteinte',
    'ACCOUNT_LOCKED': 'Compte verrouillé temporairement',
}

INFO_MESSAGES = {
    'LOGIN_SUCCESS': 'Connexion réussie',
    'LOGOUT_SUCCESS': 'Déconnexion réussie',
    'PASSWORD_RESET_REQUESTED': 'Demande de réinitialisation du mot de passe',
    'EMAIL_VERIFIED': 'Email vérifié avec succès',
    '2FA_ENABLED': 'Authentification à deux facteurs activée',
    '2FA_DISABLED': 'Authentification à deux facteurs désactivée',
}



