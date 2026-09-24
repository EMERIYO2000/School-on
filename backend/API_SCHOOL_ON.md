# API School On — version frontend

Voici les endpoints les plus utiles pour le front-end, en partant de ce qui est déjà réellement fonctionnel dans le backend.

## 1. Base URL

- API principale : `/api/`
- Cours : `/api/courses/`
- Paiements : `/api/payments/`

Header requis pour les endpoints protégés :

```http
Authorization: Bearer <access_token>
```

---

## 2. Authentification

### 2.1 Inscription

- URL : `/api/auth/register/`
- Méthode : `POST`
- Auth : public

Exemple :

```json
{
  "full_name": "Aminata Diallo",
  "email": "aminata@example.com",
  "password": "MotDePasse123!",
  "confirm_password": "MotDePasse123!",
  "phone_number": "+221770000000",
  "user_type": "STUDENT"
}
```

Réponse attendue :

```json
{
  "message": "Compte créé avec succès !",
  "user": {
    "id": 1,
    "email": "aminata@example.com",
    "full_name": "Aminata Diallo",
    "username": "aminata@example.com",
    "user_type": "STUDENT",
    "is_parent": false,
    "is_teacher": false
  },
  "access": "...",
  "refresh": "..."
}
```

### 2.2 Connexion

- URL : `/api/auth/login/`
- Méthode : `POST`
- Auth : public

Exemple :

```json
{
  "login_id": "aminata@example.com",
  "password": "MotDePasse123!"
}
```

### 2.3 Récupérer le profil connecté

- URL : `/api/auth/me/`
- Méthode : `GET`
- Auth : oui

### 2.4 Rafraîchir le token

- URL : `/api/auth/token/refresh/`
- Méthode : `POST`
- Auth : public

Exemple :

```json
{
  "refresh": "<refresh_token>"
}
```

### 2.5 Changer le mot de passe

- URL : `/api/auth/change-password/`
- Méthode : `POST`
- Auth : oui

Exemple :

```json
{
  "older_password": "AncienMotDePasse123!",
  "new_password": "NouveauMotDePasse123!",
  "confirm_password": "NouveauMotDePasse123!"
}
```

### 2.6 Demande de reset

- URL : `/api/auth/password-reset-request/`
- Méthode : `POST`
- Auth : public

Exemple :

```json
{
  "email": "aminata@example.com"
}
```

### 2.7 Validation OTP + nouveau mot de passe

- URL : `/api/auth/password-reset-confirm/`
- Méthode : `POST`
- Auth : public

Exemple :

```json
{
  "email": "aminata@example.com",
  "code": "123456",
  "new_password": "NouveauMotDePasse123!"
}
```

---

## 3. Profil utilisateur

### 3.1 Profil complet

- URL : `/api/profile/me/`
- Méthode : `GET`
- Auth : oui

### 3.2 Modifier l’avatar

- URL : `/api/profile/avatar/`
- Méthode : `POST`
- Auth : oui
- Type : `multipart/form-data`

### 3.3 Mettre à jour le profil tuteur

- URL : `/api/profile/tutor/`
- Méthodes : `PATCH`, `PUT`
- Auth : oui + compte enseignant

### 3.4 Position GPS

- URL : `/api/profile/location/`
- Méthode : `PATCH`
- Auth : oui

Exemple :

```json
{
  "latitude": -3.367,
  "longitude": 29.363
}
```

---

## 4. Utilisateurs avancés

### 4.1 Définir le token FCM

- URL : `/api/users/me/fcm-token/`
- Méthode : `POST`
- Auth : oui

Exemple :

```json
{
  "fcm_token": "token_firebase_du_device"
}
```

### 4.2 Mettre à jour la position GPS

- URL : `/api/users/me/location/`
- Méthode : `PATCH`
- Auth : oui

### 4.3 Demande de rattachement parent → enfant

- URL : `/api/users/parent-child/request/`
- Méthode : `POST`
- Auth : oui + parent

Exemple :

```json
{
  "child_identifier": "enfant@example.com"
}
```

### 4.4 Répondre à une demande

- URL : `/api/users/parent-child/respond/`
- Méthode : `POST`
- Auth : oui

Exemple :

```json
{
  "relation_id": 12,
  "action": "accept"
}
```

### 4.5 Trouver des tuteurs proches

- URL : `/api/users/nearby-tutors/`
- Méthode : `GET`
- Auth : oui

Paramètres :

```http
GET /api/users/nearby-tutors/?radius=10&lat=-3.367&lng=29.363
```

### 4.6 Désactiver mon compte

- URL : `/api/users/me/`
- Méthode : `DELETE`
- Auth : oui

### 4.7 Fermer toutes les sessions

- URL : `/api/users/logout-all/`
- Méthode : `POST`
- Auth : oui

---

## 5. Cours

### 5.1 Liste des catégories

- URL : `/api/courses/categories/`
- Méthode : `GET`
- Auth : public

### 5.2 Liste des cours

- URL : `/api/courses/courses/`
- Méthode : `GET`
- Auth : public en lecture

### 5.3 Créer un cours

- URL : `/api/courses/courses/`
- Méthode : `POST`
- Auth : oui + mentor

### 5.4 S’inscrire à un cours

- URL : `/api/courses/courses/{id}/enroll/`
- Méthode : `POST`
- Auth : oui

### 5.5 Mes cours

- URL : `/api/courses/courses/my_courses/`
- Méthode : `GET`
- Auth : oui

### 5.6 Liste des leçons

- URL : `/api/courses/lessons/`
- Méthode : `GET`
- Auth : oui

### 5.7 Marquer une leçon comme terminée

- URL : `/api/courses/lessons/{id}/mark_completed/`
- Méthode : `POST`
- Auth : oui

### 5.8 Liste des quiz

- URL : `/api/courses/quizzes/`
- Méthode : `GET`
- Auth : oui

### 5.9 Démarrer un quiz

- URL : `/api/courses/quizzes/{id}/start/`
- Méthode : `POST`
- Auth : oui

### 5.10 Soumettre un quiz

- URL : `/api/courses/quizzes/submit/{id}/`
- Méthode : `POST`
- Auth : oui

Exemple payload :

```json
{
  "attempt_id": 12,
  "answers": {
    "1": [2],
    "2": "Paris"
  }
}
```

### 5.11 Questions apprenant

- URL : `/api/courses/learner-questions/`
- Méthode : `GET`, `POST`
- Auth : oui

### 5.12 Contenu pédagogique

- URL : `/api/courses/content-blocks/`
- Méthode : `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- Auth : oui

---

## 6. Paiements

### 6.1 Créer une transaction / voir mes transactions

- URL : `/api/payments/`
- Méthodes : `GET`, `POST`
- Auth : oui

Exemple création :

```json
{
  "course": 1,
  "amount": 25000,
  "currency": "XOF",
  "payment_method": "TEST"
}
```

### 6.2 Détail d’une transaction

- URL : `/api/payments/{transaction_id}/`
- Méthode : `GET`
- Auth : oui

### 6.3 Remboursement

- URL : `/api/payments/{transaction_id}/refund/`
- Méthode : `POST`
- Auth : oui

### 6.4 Confirmation booking

- URL : `/api/payments/bookings/{booking_id}/student-confirm/`
- URL : `/api/payments/bookings/{booking_id}/mentor-confirm/`
- Méthode : `POST`
- Auth : oui

---

## 7. Endpoints utiles à garder en tête

- `/api/auth/register/`
- `/api/auth/login/`
- `/api/auth/me/`
- `/api/profile/me/`
- `/api/users/me/location/`
- `/api/courses/courses/`
- `/api/courses/courses/{id}/enroll/`
- `/api/courses/quizzes/{id}/start/`
- `/api/courses/quizzes/submit/{id}/`
- `/api/payments/`

---

## 8. Documentation Swagger

- `/schema/`
- `/swagger/`
- `/redoc/`

---

## 9. Remarque

Les routes ci-dessus correspondent à l’API réellement exposée dans le projet. Elles sont les plus importantes à utiliser côté front-end pour les fonctionnalités de base.


### 6.6 Simulation de paiement de test

- Méthode : `POST`
- Route : `/api/payments/test/<transaction_id>/simulate/`
- Accès : admin uniquement

---

## 7. Points de vigilance

- Plusieurs routes sont déclarées avec alias sans slash (`/api/auth/register`, `/api/auth/login`) pour compatibilité client.
- Certaines routes fonctionnent avec `@action` et ne sont pas des routes REST standard classiques.
- Les endpoints sont bien exposés dans les fichiers `urls.py` ; ils correspondent à la vraie API active du projet.
- Le fichier `school_on_backend/school_on/urls.py` inclut aussi les routes Swagger/OpenAPI :
  - `/schema/`
  - `/swagger/`
  - `/redoc/`

---

## 8. Vue synthétique

Routes actives par domaine :

- Authentification : 9 endpoints principaux
- Profil : 5 endpoints
- Utilisateur avancé : 8 endpoints
- Cours : 9 ressources + actions
- Paiements : 5 endpoints

La liste ci-dessus reflète les points d’entrée réellement disponibles dans le backend au moment de cette documentation.
- `level`

Exemples :

```http
GET /api/courses/courses/?category=maths
GET /api/courses/courses/?state_exam=true
GET /api/courses/courses/?level=beginner
```

### 5.3 Détail d’un cours

- `GET /api/courses/courses/{id}/`
- Accès : public

### 5.4 S’inscrire à un cours

- `POST /api/courses/courses/{id}/enroll/`
- Accès : authentifié

Le comportement implémenté est :

- cours gratuit → statut `active`
- cours premium → statut `pending`

### 5.5 Mes cours

- `GET /api/courses/courses/my_courses/`
- Accès : authentifié

### 5.6 Leçons

- `GET /api/courses/lessons/`
- Accès : authentifié

La logique de visibilité est :

- enseignant : voit seulement ses propres leçons
- apprenant : voit seulement les leçons des cours auxquels il est inscrit

### 5.7 Marquer une leçon comme terminée

- `POST /api/courses/lessons/{id}/mark_completed/`
- Accès : authentifié

### 5.8 Quiz

- `GET /api/courses/quizzes/`
- Accès : authentifié

### 5.9 Soumettre un quiz

- `POST /api/courses/quizzes/submit/{quiz_id}/`
- Accès : authentifié

Payload :

```json
{
  "answers": {
    "1": 4,
    "2": 9,
    "3": 7
  }
}
```

Réponse type :

```json
{
  "attempt_id": 4,
  "score": 66.67,
  "xp_earned": 0,
  "details": [
    {
      "question_id": 1,
      "is_correct": true,
      "explanation": "Explication de la réponse"
    }
  ]
}
```

---

## 6. Documentation OpenAPI

La documentation Swagger est disponible sur :

- `/swagger/`
- `/redoc/`
- `/schema/`

---

## 7. Points importants à retenir

- Les routes `/api/auth/register/` et `/api/auth/login/` renvoient `access` et `refresh` directement à la racine.
- Les endpoints d’authentification sont publics.
- Les routes protégées utilisent le header `Authorization: Bearer <token>`.
- La logique parent/enfant est répartie entre `/api/profile` et `/api/users`.
- L’intégration Firebase FCM est présente, mais le fichier local `firebase_credentials.json` est requis pour fonctionner en local.
- Le backend utilisateur est globalement fonctionnel ; les améliorations à prévoir concernent surtout la robustesse des validations, le standard des réponses et la documentation d’erreur.

---

## 8. Flux de travail typique

### Inscription + connexion

1. `POST /api/auth/register/`
2. Récupérer `access` et `refresh`
3. Utiliser le token sur les endpoints protégés
4. `POST /api/auth/login/` si besoin de reconnecter

### Profil

1. `GET /api/auth/me/`
2. `GET /api/profile/me/`
3. `PATCH /api/profile/location/`
4. `PATCH /api/users/me/location/`

### Rattachement parent/enfant

1. `POST /api/users/parent-child/request/`
2. L’enfant reçoit la demande
3. `POST /api/users/parent-child/respond/` avec `action` = `accept` ou `reject`

---

## 9. Exemple complet de flux client

```http
# 1. Inscription
POST /api/auth/register/
Content-Type: application/json

{
  "full_name": "Aminata Diallo",
  "email": "aminata@example.com",
  "password": "MotDePasse123!",
  "confirm_password": "MotDePasse123!",
  "phone_number": "+221770000000",
  "user_type": "STUDENT"
}

# 2. Réponse attendue
{
  "message": "Compte créé avec succès !",
  "user": {
    "id": 1,
    "email": "aminata@example.com",
    "full_name": "Aminata Diallo",
    "username": "aminata@example.com"
  },
  "access": "eyJ...",
  "refresh": "eyJ..."
}

# 3. Appel authentifié
GET /api/auth/me/
Authorization: Bearer <access>
```

---

## 10. Remarques de développement

- Cette API est conçue pour un app mobile ou web.
- Les JWT sont utilisés comme mécanisme principal d’authentification.
- Le stockage de fichiers est pris en charge sur les profils et tutor-documents.
- Les notifications push FCM peuvent être activées via un fichier de credentials Firebase local.
- Les routes de profil et de fonctionnalités avancées sont séparées pour un meilleur découpage métier.
