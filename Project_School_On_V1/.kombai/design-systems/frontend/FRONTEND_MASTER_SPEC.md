# SCHOOL ON — FRONTEND MASTER SPEC

> **Une plateforme intelligente pour apprendre, enseigner et s'entraider.**

**Document maître — Frontend React.js + Tailwind CSS**

| Information            | Valeur                                             |
| ---------------------- | -------------------------------------------------- |
| Projet                 | SCHOOL ON                                          |
| Document               | FRONTEND MASTER SPEC                               |
| Version                | 1.0                                                |
| Statut                 | Specification de référence                         |
| Frontend               | React.js                                           |
| Styling                | Tailwind CSS                                       |
| Backend                | Django / API                                       |
| Cible                  | Web responsive                                     |
| Outil d'implémentation | Kombai AI                                          |
| Audience               | Frontend, Backend, UI/UX, Product, AI Coding Agent |

---

# 1. OBJECTIF DU DOCUMENT

Ce document constitue la **source de vérité du frontend SCHOOL ON**.

Il doit permettre à un développeur humain ou à un agent IA comme Kombai de comprendre :

* ce qu'est SCHOOL ON ;
* qui utilise l'application ;
* comment les utilisateurs entrent dans l'application ;
* comment fonctionne l'authentification ;
* comment les rôles sont déterminés ;
* quelles pages existent ;
* quelles fonctionnalités appartiennent à chaque rôle ;
* comment les parcours utilisateur fonctionnent ;
* comment les cours, quiz, examens et certifications s'intègrent ;
* comment les mentors sont vérifiés ;
* comment les réservations et paiements s'intègrent ;
* comment le design system doit être appliqué ;
* comment l'application doit se comporter sur mobile, tablette et desktop ;
* quelles règles de sécurité le frontend doit respecter ;
* ce que Kombai peut générer et ce qu'il ne doit jamais inventer.

Ce document ne remplace pas les spécifications détaillées des modules.

Il les **orchestre au niveau frontend**.

---

# 2. DOCUMENTS DE RÉFÉRENCE

Le frontend doit respecter les documents fonctionnels existants.

Documents principaux :

```text
SCHOOL_ON_User_Mentor_Journey.md
        ↓
Authentification + inscription + parcours Mentor
```

```text
SCHOOL_ON_Learning_Quiz_Engine.md
        ↓
Cours + contenu + progression + quiz
```

```text
Système_de_Certification_des_Cours.md
        ↓
Certification + certificat + QR + vérification
```

```text
SCHOOL_ON_Vision_Strategie_et_Architecture.md
        ↓
Vision + sécurité + mentorat + paiement + confiance
```

Ces documents constituent les références fonctionnelles.

**Kombai ne doit pas réinventer les règles métier déjà définies dans ces documents.**

---

# 3. VISION PRODUIT

SCHOOL ON est une plateforme permettant de réunir :

```text
CONTENU
   +
PRATIQUE
   +
ACCOMPAGNEMENT HUMAIN
   +
COMMUNAUTÉ
   +
PROGRESSION
```

L'expérience centrale doit permettre à l'apprenant de :

```text
Identifier un besoin
        ↓
Trouver quoi apprendre
        ↓
Suivre un cours
        ↓
Pratiquer
        ↓
Faire des quiz
        ↓
Identifier ses lacunes
        ↓
Progresser
        ↓
Demander de l'aide
        ↓
Trouver un mentor si nécessaire
        ↓
Évaluer sa progression
        ↓
Obtenir une certification lorsque les conditions sont remplies
```

Le frontend doit donc être conçu autour du **parcours d'apprentissage**, et non autour d'une simple collection de pages.

---

# 4. PRINCIPES UX

## 4.1 Simplicité

L'utilisateur doit comprendre rapidement :

* où il se trouve ;
* ce qu'il peut faire ;
* quelle est la prochaine étape ;
* où retrouver son travail.

---

## 4.2 Progression visible

L'apprenant doit pouvoir voir :

```text
Cours
████████░░ 80%

Quiz
7 / 10

Progression générale
72%
```

La progression doit être visuelle mais ne doit jamais être calculée arbitrairement par le frontend.

---

## 4.3 Une action principale par écran

Chaque écran important doit avoir une action principale identifiable.

Exemple :

```text
Cours
[ Continuer le cours ]
```

plutôt que plusieurs boutons de même importance.

---

## 4.4 Mobile-first

Le design doit fonctionner correctement sur :

```text
Mobile
   ↓
Tablet
   ↓
Desktop
```

Le mobile n'est pas une version réduite du desktop.

---

## 4.5 Accessibilité

Prévoir :

* contraste suffisant ;
* tailles de texte lisibles ;
* navigation clavier ;
* focus visible ;
* labels explicites ;
* boutons accessibles ;
* messages d'erreur compréhensibles ;
* alternatives textuelles lorsque nécessaire.

---

# 5. AUTHENTIFICATION ET PARCOURS D'ENTRÉE

## 5.1 Principe fondamental

Le rôle n'est **PAS demandé à la connexion**.

La connexion répond à :

> Qui es-tu ?

Le rôle répond à :

> Quel parcours et quelles permissions possèdes-tu ?

---

# 6. PARCOURS GLOBAL D'ENTRÉE

```text
SPLASH
   ↓
WELCOME
   ↓
CONNEXION / INSCRIPTION
   ↓
COMPTE CRÉÉ
   ↓
CHOIX DU PARCOURS
   ├───────────────┬─────────────────┐
   ↓               ↓                 ↓
APPRENANT        MENTOR        DÉCIDER PLUS TARD
   ↓               ↓                 ↓
Profil simple   Candidature       Expérience
   ↓           Mentor            apprenant
   ↓               ↓
Dashboard       Vérification
                   ↓
              Review Admin
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
       APPROUVÉ           REFUSÉ
          ↓
   Mentor vérifié
          ↓
      Dashboard
```

Ce parcours est conforme au parcours utilisateur/mentor existant.

---

# 7. ADMIN : RÈGLE DE VISIBILITÉ

Le rôle ADMIN ne doit jamais apparaître comme choix public.

L'écran d'inscription ne doit jamais afficher :

```text
Je veux être :

○ Apprenant
○ Mentor
○ Administrateur
```

Il doit afficher uniquement les parcours destinés aux utilisateurs.

L'administration est une **permission interne**.

---

# 8. AUTHENTIFICATION

Le frontend doit prévoir :

```text
/login
/register
/forgot-password
/reset-password
/verify-account
```

Selon les mécanismes retenus côté backend, l'authentification pourra utiliser :

* email + mot de passe ;
* numéro de téléphone ;
* OTP ;
* Google ;
* autres méthodes ultérieures.

Le frontend ne doit pas imposer une méthode non définie par le backend.

---

# 9. SÉPARATION AUTHENTICATION / AUTHORIZATION

## Authentication

Répond :

> Qui est connecté ?

## Authorization

Répond :

> Que cette personne a-t-elle le droit de faire ?

Architecture :

```text
Browser
   ↓
React
   ↓
Django API
   ↓
Authentication
   ↓
Authorization
   ↓
Permissions
```

Le frontend peut afficher une interface adaptée au rôle.

Mais **le backend reste l'autorité finale**.

---

# 10. MODÈLE DE RÔLES

Rôles principaux :

```text
LEARNER
MENTOR
ADMIN
```

Pour les mentors, ajouter un statut distinct :

```text
PENDING
VERIFIED
SUSPENDED
REJECTED
```

Un utilisateur ayant :

```text
role = MENTOR
mentor_status = PENDING
```

ne doit pas avoir les mêmes capacités qu'un mentor vérifié.

---

# 11. MATRICE DE PERMISSIONS

Le frontend doit connaître les permissions pour construire l'interface.

Exemple :

| Fonction               | Learner | Mentor Pending |  Mentor Verified | Admin |
| ---------------------- | ------: | -------------: | ---------------: | ----: |
| Consulter les cours    |       ✅ |              ✅ |                ✅ |     ✅ |
| Suivre un cours        |       ✅ |              ✅ |                ✅ |     ✅ |
| Faire des quiz         |       ✅ |              ✅ |                ✅ |     ✅ |
| Rechercher un mentor   |       ✅ |              ✅ |                ✅ |     ✅ |
| Réserver un mentor     |       ✅ |   selon règles |                ✅ |     — |
| Créer un cours         |       ❌ |              ❌ |                ✅ |     ✅ |
| Publier un cours       |       ❌ |              ❌ | selon validation |     ✅ |
| Gérer les utilisateurs |       ❌ |              ❌ |                ❌ |     ✅ |
| Gérer les mentors      |       ❌ |              ❌ |                ❌ |     ✅ |
| Gérer les paiements    |       ❌ |              ❌ |                ❌ |     ✅ |
| Gérer les certificats  |       ❌ |              ❌ |                ❌ |     ✅ |

**Cette matrice est indicative au niveau frontend. Les permissions réelles sont décidées côté backend.**

---

# 12. ROUTING REACT

Structure logique :

```text
PUBLIC
│
├── /
├── /about
├── /privacy
├── /terms
├── /login
├── /register
└── /forgot-password

PROTECTED
│
├── /dashboard
├── /courses
├── /learning
├── /quiz
├── /exams
├── /mentors
├── /bookings
├── /community
├── /certificates
├── /profile
└── /settings

MENTOR
│
├── /mentor/dashboard
├── /mentor/courses
├── /mentor/courses/create
├── /mentor/courses/:id
├── /mentor/learners
├── /mentor/bookings
├── /mentor/earnings
├── /mentor/certificates
├── /mentor/profile
└── /mentor/verification

ADMIN
│
├── /admin/dashboard
├── /admin/users
├── /admin/mentors
├── /admin/courses
├── /admin/quizzes
├── /admin/exams
├── /admin/bookings
├── /admin/payments
├── /admin/certificates
├── /admin/reports
├── /admin/moderation
└── /admin/settings
```

---

# 13. PROTECTED ROUTES

Le frontend doit avoir une logique équivalente à :

```text
PublicRoute
ProtectedRoute
RoleRoute
PermissionRoute
```

Exemple conceptuel :

```text
ProtectedRoute
       ↓
Utilisateur connecté ?
       │
   ┌───┴───┐
   ↓       ↓
  NON     OUI
   ↓       ↓
 /login   RoleRoute
```

Puis :

```text
RoleRoute
   ├── LEARNER → Learner UI
   ├── MENTOR  → Mentor UI
   └── ADMIN   → Admin UI
```

Le frontend ne doit jamais considérer cette protection comme suffisante.

Le backend doit effectuer la même vérification.

---

# 14. RÈGLE DE SÉCURITÉ ABSOLUE

> **NEVER TRUST THE CLIENT.**

Tout ce qui vient du navigateur peut être falsifié.

Le frontend ne doit jamais être l'autorité pour :

```text
role
permissions
price
commission
payment status
quiz score
course progress
certificate eligibility
certificate generation
mentor verification
booking status
identity verification
```

Le frontend :

```text
AFFICHE
DEMANDE
ENVOIE
```

Le backend :

```text
VALIDE
AUTORISE
CALCULE
DÉCIDE
```

---

# 15. SÉCURITÉ FRONTEND

## 15.1 HTTPS

Toutes les communications de production doivent utiliser HTTPS.

---

## 15.2 Tokens / sessions

Le frontend ne doit pas inventer sa propre stratégie d'authentification.

La stratégie de session/token doit être définie avec le backend.

Privilégier une architecture réduisant l'exposition des credentials côté JavaScript et navigateur.

---

## 15.3 localStorage

Ne jamais considérer :

```text
localStorage.role
localStorage.isAdmin
localStorage.isMentor
```

comme une preuve de permission.

Le frontend peut mémoriser des préférences non sensibles.

Les permissions critiques doivent provenir de l'état d'authentification fourni par le backend.

---

## 15.4 Secrets

Aucune clé secrète ne doit être intégrée au bundle React.

Ne jamais mettre dans le frontend :

```text
DATABASE_PASSWORD
DJANGO_SECRET_KEY
PRIVATE_API_KEY
PAYMENT_PRIVATE_KEY
WEBHOOK_SECRET
```

Une variable exposée au navigateur doit être considérée comme publique.

---

# 16. XSS ET CONTENU UTILISATEUR

SCHOOL ON contient beaucoup de contenu généré par :

* mentors ;
* administrateurs ;
* apprenants ;
* communauté.

Donc attention aux :

```text
descriptions
commentaires
questions
réponses
articles
contenus de cours
```

Éviter l'injection directe de HTML non contrôlé.

Toute fonctionnalité nécessitant du HTML riche doit utiliser une stratégie de sanitation appropriée côté système.

---

# 17. VALIDATION DES DONNÉES

Toujours :

```text
Frontend validation
       +
Backend validation
```

Exemple :

```text
Frontend
→ email invalide
→ message immédiat

Backend
→ validation réelle
→ accepte ou refuse
```

La validation frontend améliore l'expérience.

La validation backend assure l'intégrité.

---

# 18. UPLOADS

SCHOOL ON peut recevoir :

```text
photo
PDF
vidéo
document
signature
document d'identité
certificat
fichier de cours
```

Le frontend doit contrôler :

* taille ;
* format attendu ;
* extension ;
* progression de l'upload ;
* erreurs.

Mais le backend doit également vérifier les fichiers.

Ne jamais considérer :

```text
file.name = "document.pdf"
```

comme une preuve que le fichier est réellement un PDF.

---

# 19. DONNÉES SENSIBLES

Certaines données doivent être considérées comme privées :

```text
documents d'identité
adresse exacte
documents professionnels
données de vérification
selfies/vidéos de vérification
notes administratives
```

Ces informations ne doivent jamais être exposées par défaut dans le profil public.

Le document de parcours Mentor établit explicitement la séparation entre informations publiques et privées.

---

# 20. PROFIL MENTOR

Profil public :

```text
Nom
Photo
Bio
Ville
Domaines
Compétences
Expérience
Badge de vérification
Avis
Statistiques pertinentes
```

Profil privé :

```text
Documents d'identité
Adresse exacte
Numéro de document
Documents de vérification
Notes administratives
```

L'adresse exacte ne doit pas devenir une information publique.

---

# 21. MENTORAT ET SÉCURITÉ

Le frontend doit respecter le principe :

> **La localisation sert à faciliter un accompagnement, pas à permettre de localiser librement des personnes.**

Pour une réservation :

```text
Recherche mentor
      ↓
Domaine
      ↓
Mode
(en ligne / présentiel)
      ↓
Date
      ↓
Durée
      ↓
Demande
      ↓
Acceptation mentor
      ↓
Session
      ↓
Confirmation
```

Les informations de localisation doivent être minimisées.

Le système doit favoriser des lieux appropriés et sûrs lorsque des rencontres physiques sont proposées.

---

# 22. DASHBOARD APPRENANT

Le dashboard doit répondre rapidement à :

> Que dois-je faire maintenant ?

Structure indicative :

```text
Header
   ↓
Bonjour, [Nom]
   ↓
Continuer l'apprentissage
   ↓
Progression
   ↓
Cours en cours
   ↓
Quiz / examens
   ↓
Mentors recommandés
   ↓
Réservations
   ↓
Certifications
   ↓
Activité récente
```

Le dashboard ne doit pas devenir une page remplie de statistiques inutiles.

---

# 23. DASHBOARD MENTOR

Le dashboard Mentor doit répondre à :

> Que dois-je gérer aujourd'hui ?

Sections :

```text
Vue générale
Cours
Apprenants
Questions
Quiz
Réservations
Certifications
Revenus
Profil
Vérification
```

Si le mentor est encore `PENDING`, l'interface doit clairement afficher son état.

---

# 24. DASHBOARD ADMIN

L'Admin dispose d'une interface distincte.

Sections :

```text
Dashboard
Utilisateurs
Mentors
Cours
Quiz
Examens
Réservations
Paiements
Certificats
Modération
Rapports
Paramètres
```

L'interface Admin ne doit jamais être présentée comme un rôle public lors de l'inscription.

---

# 25. COURS

Un cours n'est pas simplement :

```text
Titre
Vidéo
Fin
```

Il est structuré :

```text
Course
  │
  ├── Chapter
  │      ├── Content
  │      ├── Content
  │      └── Quiz
  │
  ├── Chapter
  │      ├── Content
  │      └── Quiz
  │
  └── Final Assessment
```

Les contenus peuvent inclure :

```text
Text
Image
Video
Document
Code
Quiz
```

---

# 26. PAGE COURSE DETAIL

Doit présenter :

```text
Titre
Description
Mentor
Niveau
Durée
Objectifs
Programme
Nombre de chapitres
Évaluation
Certification éventuelle
Prix
Progression
```

Action principale :

```text
Commencer
```

ou :

```text
Continuer
```

selon l'état de l'apprenant.

---

# 27. LEARNING EXPERIENCE

Structure :

```text
Course
   ↓
Chapter
   ↓
Lesson content
   ↓
Progression
   ↓
Quiz
   ↓
Résultat
   ↓
Chapter suivant
```

L'interface doit conserver le contexte :

```text
Cours
→ Chapitre
→ Leçon actuelle
→ Progression
```

---

# 28. QUIZ ENGINE

SCHOOL ON doit utiliser un **moteur de quiz réutilisable**.

Ne pas créer :

```text
CourseQuiz
GameQuiz
ExamQuiz
TrainingQuiz
```

comme quatre systèmes frontend indépendants.

Créer un moteur réutilisable :

```text
QuizEngine
```

qui peut être configuré selon le contexte.

---

# 29. QUIZ CONTEXTES

Le même moteur peut servir pour :

```text
Course Quiz
Quiz Game
Quiz Training
Exam Preparation
Assessment
Final Assessment
```

---

# 30. QUIZ FLOW

```text
Quiz intro
   ↓
Question
   ↓
Réponse
   ↓
Question suivante
   ↓
...
   ↓
Submit
   ↓
Correction
   ↓
Résultat
   ↓
Explication
   ↓
Historique
```

Le frontend ne doit jamais déterminer lui-même la réponse correcte.

Le backend reste la source de vérité.

---

# 31. TYPES DE QUESTIONS

Le frontend doit pouvoir supporter les types définis par le moteur :

```text
Single Choice
Multiple Choice
```

et être extensible pour les futurs types.

Le composant de question doit être découplé du reste du QuizEngine.

---

# 32. EXAMENS

Section dédiée :

```text
Exam Home
   ↓
Subject
   ↓
Test
   ↓
Questions
   ↓
Submit
   ↓
Result
   ↓
Weaknesses
```

L'interface doit permettre de comprendre :

```text
Score
Questions correctes
Questions incorrectes
Temps
Domaines faibles
Progression
```

---

# 33. MENTORS

Page :

```text
/mentors
```

Fonctions :

```text
Recherche
Filtre
Domaine
Compétence
Ville
Mode
Disponibilité
```

Carte Mentor :

```text
Photo
Nom
Badge
Domaine
Expérience
Avis
Disponibilité
[Voir profil]
```

---

# 34. BOOKING

Flow :

```text
Mentor Profile
     ↓
Book Session
     ↓
Mode
     ↓
Date
     ↓
Durée
     ↓
Confirmation
     ↓
Paiement si nécessaire
     ↓
Booking status
```

États possibles :

```text
PENDING
ACCEPTED
IN_PROGRESS
COMPLETED
DISPUTED
REFUNDED
CANCELLED
```

Le frontend doit refléter les statuts fournis par l'API.

Il ne doit pas modifier lui-même le statut.

---

# 35. PAIEMENTS

Le frontend ne doit jamais décider qu'une transaction est réussie.

Il doit afficher :

```text
PENDING
PROCESSING
SUCCESS
FAILED
CANCELLED
REFUNDED
```

Architecture :

```text
Frontend
   ↓
Payment request
   ↓
Backend
   ↓
Provider
   ↓
Verification / Webhook
   ↓
Backend transaction status
   ↓
Frontend
```

---

# 36. CERTIFICATION

La certification doit être intégrée au parcours du cours.

```text
Course
   ↓
Progression
   ↓
Content completed
   ↓
Quiz
   ↓
Final assessment/project
   ↓
Conditions remplies
   ↓
Mentor validation si nécessaire
   ↓
Certificate
```

Le frontend ne doit jamais permettre à l'utilisateur de déclarer :

```text
"I passed"
```

pour obtenir un certificat.

---

# 37. CERTIFICATE UI

Learner :

```text
My Certificates
       ↓
Certificate Card
       ↓
Certificate Detail
       ↓
View
Download
Print
Share
Verify
```

Le certificat doit présenter notamment :

```text
Nom apprenant
Cours
Mentor
Date
Niveau
Certificate ID
Signature mentor
Signature School On
QR Code
```

Le système de certification existant prévoit également une vérification publique via identifiant unique et QR Code.

---

# 38. CERTIFICATE VERIFICATION

Route publique :

```text
/verify/:certificateId
```

La page affiche uniquement les informations destinées à la vérification publique.

Elle ne doit pas exposer :

```text
documents privés
adresse
données sensibles
informations internes
```

---

# 39. COMMUNITY

Prévoir :

```text
Community Home
Post
Discussion
Comments
Questions
Reports
```

Les interactions communautaires doivent avoir :

```text
Loading
Empty
Error
Success
Report
Block
```

---

# 40. PROFILE

## Learner

```text
Photo
Nom
Bio
Progression
Cours
Certificats
Activité
Paramètres
```

## Mentor

```text
Profil public
Bio
Compétences
Expérience
Cours
Disponibilités
Avis
Vérification
Documents privés
```

Les documents privés ne doivent jamais être affichés dans le profil public.

---

# 41. DESIGN SYSTEM

Le design system doit être défini avant de générer toutes les pages.

Il doit couvrir :

```text
Colors
Typography
Spacing
Radius
Shadows
Icons
Buttons
Inputs
Cards
Modals
Tabs
Badges
Alerts
Tables
Dropdowns
Navigation
Progress bars
Skeletons
```

Tailwind CSS doit **implémenter** le design system.

Tailwind n'est pas lui-même le design system.

---

# 42. DESIGN TOKENS

Créer des tokens centralisés :

```text
Primary
Secondary
Background
Surface
Text
Muted
Border
Success
Warning
Error
Info
```

Même logique pour :

```text
spacing
radius
shadow
typography
breakpoints
```

Éviter de disperser arbitrairement des valeurs différentes dans toute l'application.

---

# 43. COMPOSANTS UI

Créer des composants réutilisables :

```text
Button
Input
Select
Textarea
Checkbox
Radio
Modal
Dialog
Card
Badge
Avatar
Tabs
Dropdown
Toast
Alert
Tooltip
Pagination
Skeleton
EmptyState
ErrorState
Progress
```

---

# 44. COMPOSANTS MÉTIER

Créer ensuite :

```text
CourseCard
CourseProgress
ChapterNavigation
QuizQuestion
QuizOption
QuizResult
MentorCard
MentorProfile
BookingCard
PaymentStatus
CertificateCard
CertificatePreview
VerificationBadge
```

Les composants métier doivent réutiliser les composants UI.

---

# 45. ÉTATS UI OBLIGATOIRES

Chaque fonctionnalité importante doit prévoir :

```text
Default
Loading
Empty
Error
Success
Disabled
Unauthorized
Forbidden
```

Exemple :

```text
Cours en chargement
Cours vide
Cours indisponible
Erreur réseau
Utilisateur non autorisé
```

Ne jamais concevoir uniquement le "happy path".

---

# 46. API CONTRACT

Le frontend ne doit pas inventer la structure des données.

Pour chaque module, documenter :

```text
Endpoint
Method
Request
Response
Authentication
Permissions
Errors
Loading state
```

Exemple :

```text
GET /api/auth/me
```

Retour conceptuel :

```json
{
  "id": 1,
  "name": "User",
  "role": "LEARNER"
}
```

Mais le format final doit être celui défini avec le backend.

---

# 47. ARCHITECTURE REACT

Structure recommandée :

```text
src/
│
├── app/
│   ├── router/
│   ├── providers/
│   └── layouts/
│
├── components/
│   ├── ui/
│   ├── navigation/
│   ├── courses/
│   ├── quizzes/
│   ├── mentors/
│   ├── bookings/
│   ├── certificates/
│   └── community/
│
├── features/
│   ├── auth/
│   ├── learner/
│   ├── mentor/
│   ├── admin/
│   ├── courses/
│   ├── quiz/
│   ├── exams/
│   ├── mentors/
│   ├── bookings/
│   ├── payments/
│   └── certification/
│
├── pages/
│
├── services/
│   └── api/
│
├── hooks/
│
├── lib/
│
├── types/
│
└── assets/
```

---

# 48. LAYOUTS

Prévoir au minimum :

```text
PublicLayout
LearnerLayout
MentorLayout
AdminLayout
AuthLayout
```

Chaque layout possède :

* navigation ;
* header ;
* responsive behavior ;
* breadcrumbs si nécessaire ;
* notifications ;
* user menu.

---

# 49. RESPONSIVE DESIGN

Breakpoints à définir dans le design system.

Le comportement doit être pensé pour :

```text
Mobile
Tablet
Desktop
Large Desktop
```

Exemples :

Desktop :

```text
Sidebar
Main content
Secondary panel
```

Mobile :

```text
Top bar
Main content
Bottom navigation ou menu
```

Ne pas simplement réduire les dimensions desktop.

---

# 50. PERFORMANCE FRONTEND

Prévoir :

```text
Lazy loading
Code splitting
Image optimization
Pagination
Skeleton loading
Debouncing search
Caching lorsque pertinent
Optimistic UI uniquement lorsque sûr
```

Attention :

Une optimisation frontend ne doit jamais compromettre la sécurité ou l'intégrité des données.

---

# 51. GESTION DES ERREURS

Types d'erreurs :

```text
Network error
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests
500 Server Error
```

L'utilisateur doit recevoir un message compréhensible.

Les informations techniques sensibles ne doivent pas être exposées.

---

# 52. 401 VS 403

Le frontend doit distinguer :

### 401

```text
Non authentifié
```

→ redirection vers connexion.

### 403

```text
Authentifié mais interdit
```

→ page ou composant `Forbidden`.

Exemple :

```text
Vous n'avez pas accès à cette page.
```

---

# 53. ADMIN SECURITY UX

Même si quelqu'un accède à :

```text
/admin
```

le frontend doit vérifier l'état d'authentification et les permissions.

Mais surtout :

```text
React protection
        +
Django permission protection
```

Les deux doivent exister.

La protection React améliore l'expérience.

La protection Django assure la sécurité réelle.

---

# 54. NE PAS CACHER DES SECRETS DANS LE FRONTEND

Le frontend peut contenir :

```text
public API configuration
UI configuration
feature flags non sensibles
```

Il ne doit pas contenir :

```text
database credentials
private keys
secret tokens
payment secrets
admin secrets
webhook secrets
```

---

# 55. NE PAS FAIRE CONFIANCE AUX DONNÉES CLIENT

Exemples interdits :

```text
localStorage.isAdmin === true
```

pour autoriser une action.

```text
frontendScore >= 70
```

pour générer un certificat.

```text
frontendPaymentStatus === "success"
```

pour débloquer un cours payant.

```text
frontendRole === "MENTOR"
```

pour autoriser la création d'un cours.

Ces informations doivent être validées côté backend.

---

# 56. STRUCTURE DU PROJET KOMBAI

Le dossier `.kombai` doit être organisé afin que l'agent dispose d'un contexte clair.

```text
.kombai/
│
├── canvas/
│   ├── 00-product-map
│   ├── 01-user-flows
│   ├── 02-information-architecture
│   ├── 03-screen-map
│   └── 04-responsive-layouts
│
├── design-system/
│   ├── 01-brand.md
│   ├── 02-colors.md
│   ├── 03-typography.md
│   ├── 04-spacing.md
│   ├── 05-radius.md
│   ├── 06-shadows.md
│   ├── 07-icons.md
│   ├── 08-components.md
│   └── 09-states.md
│
├── product/
│   ├── product-context.md
│   ├── roles-and-permissions.md
│   ├── navigation.md
│   └── business-rules.md
│
└── frontend/
    ├── FRONTEND_MASTER_SPEC.md
    ├── architecture.md
    ├── routes.md
    ├── components.md
    ├── api-contract.md
    └── implementation-rules.md
```

---

# 57. CANVAS

Le Canvas doit représenter l'application avant l'implémentation.

Il doit contenir :

```text
Product Map
User Flows
Information Architecture
Screen Map
Responsive Layouts
```

Il doit permettre de répondre visuellement à :

> Où suis-je ?

> Où puis-je aller ?

> Comment j'arrive ici ?

> Quelle est l'étape suivante ?

---

# 58. SCREEN MAP

Le frontend doit être construit à partir d'un inventaire d'écrans.

### Public

```text
Splash
Welcome
About
Privacy
Terms
Login
Register
Forgot Password
```

### Learner

```text
Dashboard
Courses
Course Detail
Learning
Chapter
Quiz
Quiz Result
Exams
Mentors
Mentor Profile
Booking
Community
Certificates
Certificate Detail
Profile
Settings
```

### Mentor

```text
Dashboard
Courses
Create Course
Course Editor
Quiz Management
Community
Learners
Questions
Bookings
Earnings
Certificates
Profile
Verification
Settings
```

### Admin

```text
Dashboard
Users
Mentors
Courses
Quizzes
Exams
Bookings
Community
Payments
Certificates
Reports
Moderation
Settings
```

---

# 59. RÈGLES POUR KOMBAI

Kombai doit :

```text
✓ respecter le design system
✓ respecter les routes
✓ respecter les rôles
✓ respecter les permissions
✓ réutiliser les composants
✓ produire du React propre
✓ utiliser Tailwind
✓ penser responsive
✓ prévoir loading/error/empty states
✓ utiliser les API contracts
✓ ne pas inventer de logique métier
```

---

# 60. KOMBAI NE DOIT PAS

Kombai ne doit pas :

```text
✗ inventer un rôle
✗ créer un accès Admin public
✗ considérer localStorage comme une autorité
✗ inventer des permissions
✗ inventer des endpoints
✗ inventer des données métier
✗ décider qu'un paiement est réussi
✗ décider qu'un quiz est réussi
✗ générer un certificat lui-même
✗ contourner les protections backend
✗ exposer des données privées
✗ créer des secrets côté frontend
✗ mélanger les layouts Learner/Mentor/Admin
✗ créer trois systèmes de quiz différents
```

---

# 61. PRINCIPLE OF SOURCE OF TRUTH

Pour chaque question :

```text
Question UX
     ↓
Frontend specification

Question métier
     ↓
Product specification

Question données
     ↓
Backend/API specification

Question permission
     ↓
Backend authorization

Question design
     ↓
Design system

Question architecture
     ↓
Frontend architecture
```

Kombai ne doit pas résoudre seul une contradiction.

Il doit signaler :

```text
SPECIFICATION CONFLICT
```

et demander une décision.

---

# 62. ORDRE D'IMPLÉMENTATION

Ne pas demander à Kombai :

> "Build the entire SCHOOL ON application."

Procéder par étapes.

### Phase 1 — Foundation

```text
React
Tailwind
Routing
Layouts
Design tokens
UI components
```

### Phase 2 — Authentication

```text
Welcome
Login
Register
Account creation
Choose journey
Protected routes
Role-aware layouts
```

### Phase 3 — Learner

```text
Dashboard
Courses
Learning
Quiz
Exams
Mentors
Bookings
Community
Certificates
Profile
```

### Phase 4 — Mentor

```text
Mentor dashboard
Verification
Courses
Course creation
Quiz management
Bookings
Learners
Earnings
Certificates
```

### Phase 5 — Admin

```text
Admin dashboard
Users
Mentors
Moderation
Courses
Payments
Certificates
Reports
```

### Phase 6 — Polish

```text
Responsive
Accessibility
Loading
Empty states
Error states
Performance
Animations
Micro-interactions
```

---

# 63. STRATÉGIE D'ANIMATION

Les animations doivent servir :

```text
navigation
feedback
progression
confirmation
orientation
```

Pas simplement décorer l'application.

Exemples :

```text
Page transition
Modal
Toast
Progress animation
Quiz feedback
Certificate reveal
```

Les animations doivent rester rapides et accessibles.

---

# 64. PRINCIPLE MOBILE

Sur mobile, prioriser :

```text
Navigation
Cours
Quiz
Mentors
Bookings
Certificates
Profile
```

Les dashboards complexes doivent être adaptés plutôt que simplement compressés.

---

# 65. ÉTAT GLOBAL DE L'APPLICATION

Le frontend doit pouvoir connaître au minimum :

```text
auth state
user
role
mentor status
permissions
loading state
notifications
```

Exemple conceptuel :

```text
AuthContext / Auth Store

user
isAuthenticated
role
mentorStatus
permissions
loading
```

Le choix technique final du state management doit être décidé lors de l'implémentation.

---

# 66. RÈGLE SUR LE PROFIL ET LE RÔLE

Le profil utilisateur et le rôle ne sont pas la même chose.

Un utilisateur peut :

```text
avoir un compte
      ↓
utiliser SCHOOL ON comme apprenant
      ↓
décider plus tard de devenir mentor
      ↓
soumettre une candidature
      ↓
être vérifié
```

Le frontend doit donc éviter une architecture où :

```text
Register Learner
Register Mentor
```

créent deux systèmes de comptes totalement séparés.

Le parcours Mentor est un **processus complémentaire** du compte utilisateur.

---

# 67. FUTURE PARENT ROLE

Le compte Parent n'est pas inclus dans le MVP actuel.

Architecture à garder extensible :

```text
LEARNER
MENTOR
ADMIN
```

puis ultérieurement :

```text
PARENT
```

Le frontend ne doit donc pas être codé de manière à rendre l'ajout futur d'un rôle impossible.

---

# 68. SECURITY CHECKLIST

Avant chaque release frontend :

```text
[ ] HTTPS en production
[ ] Aucun secret dans le frontend
[ ] Routes protégées
[ ] Admin non public
[ ] Permissions vérifiées côté backend
[ ] Aucun rôle basé uniquement sur localStorage
[ ] Aucun paiement validé côté frontend
[ ] Aucun certificat généré par le frontend
[ ] Aucun score considéré comme définitif côté frontend
[ ] Données sensibles non exposées
[ ] Uploads validés côté backend
[ ] Contenu utilisateur correctement traité
[ ] 401 correctement géré
[ ] 403 correctement géré
[ ] Erreurs sensibles non exposées
[ ] Validation frontend + backend
```

---

# 69. DEFINITION OF DONE — FRONTEND

Une fonctionnalité n'est pas terminée simplement parce que :

```text
"la page s'affiche."
```

Elle est terminée lorsqu'elle possède :

```text
UI
+
Responsive
+
Loading
+
Empty
+
Error
+
Success
+
Authorization
+
API integration
+
Accessibility
+
Security consideration
```

---

# 70. RÈGLE FINALE POUR L'ÉQUIPE

SCHOOL ON doit être construit selon cette séparation :

```text
                    USER
                     │
                     ▼
                 FRONTEND
                     │
          ┌──────────┴──────────┐
          │                     │
       UX/UI                API Request
          │                     │
          │                     ▼
          │                  BACKEND
          │                     │
          │            ┌────────┴────────┐
          │            │                 │
          │      Authentication    Authorization
          │            │                 │
          │            └────────┬────────┘
          │                     │
          │                 BUSINESS
          │                   RULES
          │                     │
          │                     ▼
          │                 DATABASE
          │
          ▼
      EXPERIENCE
```

Le frontend doit être **beau, rapide, clair et agréable**.

Mais il doit toujours considérer que :

> **la sécurité et l'intégrité des données ne reposent jamais uniquement sur le navigateur.**

---

# 71. RÉSUMÉ OPÉRATIONNEL

Avant de lancer Kombai :

```text
1. Product specifications
        ↓
2. User / Mentor Journey
        ↓
3. Learning / Quiz Engine
        ↓
4. Certification
        ↓
5. Payment / Booking
        ↓
6. FRONTEND MASTER SPEC
        ↓
7. Information Architecture
        ↓
8. Canvas
        ↓
9. Design System
        ↓
10. React Architecture
        ↓
11. API Contract
        ↓
12. Kombai implementation
```

Kombai intervient principalement à partir de l'étape d'implémentation.

Il ne doit pas être utilisé pour décider de la logique produit.

---

# 72. RÈGLE D'OR DE SCHOOL ON

```text
              DESIGN
                 +
                UX
                 +
              FRONTEND
                 +
              BACKEND
                 +
             SECURITY
                 +
          BUSINESS RULES
                 │
                 ▼
              SCHOOL ON
```

Aucune couche ne doit être conçue comme un système isolé.

Chaque écran frontend doit correspondre à une fonctionnalité réelle, à une règle métier claire et à un contrat API défini.

**Le frontend représente SCHOOL ON.
Le backend protège SCHOOL ON.
Le design system donne une cohérence à SCHOOL ON.
Et les spécifications empêchent l'IA d'inventer SCHOOL ON à notre place.**
