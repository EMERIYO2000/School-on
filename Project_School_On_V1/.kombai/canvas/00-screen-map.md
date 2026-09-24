# SCHOOL ON — Screen Map

> **Document:** `screen-map.md`  
> **Purpose:** définir l'architecture des écrans et la navigation de SCHOOL ON pour guider le design UI/UX et l'intégration frontend.  
> **Statut:** base fonctionnelle à aligner ensuite avec le design Figma.

---

## 1. Principes de navigation

SCHOOL ON doit être pensé **mobile-first**, avec une expérience inspirée de la logique de navigation de Discord : espaces clairement séparés, navigation persistante, accès rapide aux sections principales et adaptation progressive aux écrans plus larges.

Cette inspiration concerne **la logique d'organisation et de navigation**, pas une copie visuelle de Discord.

### Breakpoints fonctionnels

- **Mobile** : navigation compacte, priorité au contenu, menus accessibles par actions/bottom navigation/drawers.
- **Tablette** : navigation plus visible, panneaux secondaires pouvant être affichés simultanément.
- **Desktop** : sidebar/navigation persistante + contenu principal + panneaux contextuels lorsque nécessaire.

### Règle générale

Le responsive ne doit pas créer trois produits différents.

```text
                 SCHOOL ON
                     │
          ┌──────────┼──────────┐
          │          │          │
        Mobile     Tablet     Desktop
          │          │          │
          └──────────┼──────────┘
                     │
              même architecture
              mêmes fonctionnalités
              adaptation UI
```

---

# 2. Structure globale de l'application

## 2.1 Navigation principale

Les sections principales sont :

1. **Accueil**
2. **Apprendre**
3. **Communauté**
4. **Mentors**
5. **Progression**
6. **Profil**
7. **Wallet / Transactions** lorsque pertinent

Les fonctionnalités administratives et de gestion des mentors ne doivent pas apparaître comme des éléments standards pour tous les utilisateurs. Elles dépendent du rôle et des permissions.

---

# 3. Écrans d'accès et d'authentification

## 3.1 Splash / lancement

**Route logique :**
`/`

Contenu :

- logo SCHOOL ON ;
- chargement initial ;
- vérification de session ;
- redirection vers onboarding ou application.

Le logo définitif est fourni comme asset de design.

---

## 3.2 Onboarding

**Route logique :**
`/onboarding`

Écrans possibles :

- présentation de SCHOOL ON ;
- choix/précision des domaines d'intérêt ;
- explication de l'apprentissage ;
- explication de la communauté ;
- explication du mentorat ;
- finalisation.

L'onboarding doit rester court pour un utilisateur simple.

---

## 3.3 Authentification

Routes :

- `/login`
- `/register`
- `/forgot-password`
- `/verify-account`
- `/reset-password`

Éléments :

- email/téléphone selon le système retenu ;
- mot de passe ;
- validation ;
- récupération de compte ;
- gestion de session.

---

# 4. Accueil

**Route :**
`/home`

L'accueil sert de point d'entrée personnalisé.

### Sections possibles

- reprise du dernier cours ;
- recommandations ;
- progression ;
- cours récents ;
- activités communautaires pertinentes ;
- mentors ;
- notifications importantes.

L'accueil ne doit pas devenir un feed social généraliste. La communauté possède son propre espace.

---

# 5. Apprendre

**Route principale :**
`/learn`

## 5.1 Catalogue des cours

`/learn/courses`

Fonctions :

- recherche ;
- filtres ;
- catégories ;
- niveau ;
- durée ;
- prix ;
- cours gratuits/payants ;
- tri.

## 5.2 Détail d'un cours

`/learn/courses/:courseId`

Contenu :

- titre ;
- description ;
- mentor/auteur ;
- niveau ;
- modules ;
- durée ;
- prix ;
- progression ;
- informations de certification ;
- bouton d'inscription/achat.

## 5.3 Lecture d'un cours

`/learn/courses/:courseId/learn`

Structure :

- contenu du module ;
- navigation précédent/suivant ;
- progression ;
- ressources ;
- quiz associés ;
- validation de progression.

---

# 6. Quiz

Les quiz sont intégrés au parcours d'apprentissage.

## 6.1 Quiz

`/learn/courses/:courseId/quiz/:quizId`

L'écran doit supporter les modèles de questions définis par le système :

- choix unique ;
- choix multiple ;
- autres types de réponses si activés.

## 6.2 Résultat

`/learn/courses/:courseId/quiz/:quizId/result`

Afficher :

- score ;
- réponses correctes/incorrectes selon les règles ;
- progression ;
- validation ou échec ;
- prochaine étape.

Le résultat du quiz peut participer aux conditions de complétion du cours.

---

# 7. Certification

La certification est liée à la complétion du cours et non à une page indépendante isolée.

## 7.1 État de certification

`/learn/courses/:courseId/certificate`

États possibles :

- non éligible ;
- en attente de génération ;
- généré ;
- disponible ;
- révoqué/invalide selon les règles métier.

## 7.2 Consultation

Afficher :

- certificat ;
- identité du bénéficiaire ;
- cours ;
- mentor ;
- date ;
- identifiant/numéro du certificat ;
- signatures ;
- éléments d'authenticité.

## 7.3 Actions

- visualiser ;
- télécharger ;
- partager si prévu ;
- vérifier l'authenticité.

Le modèle visuel du certificat fourni par le produit/design servira de référence.

---

# 8. Communauté

**Route principale :**
`/community`

> La Communauté est un espace de publications éducatives et d'interactions sociales. Elle apparaît dans l'expérience de tous les profils, pas uniquement chez les apprenants.

## 8.1 Feed communautaire

`/community`

Fonctions :

- publications ;
- réactions ;
- commentaires ;
- réponses ;
- partage selon les règles du produit ;
- signalement ;
- filtres/catégories ;
- recherche.

## 8.2 Création de publication

`/community/create`

Une publication doit obligatoirement rester dans le périmètre éducatif de SCHOOL ON.

Exemples :

- question ;
- explication ;
- ressource ;
- conseil d'apprentissage ;
- retour d'expérience pédagogique ;
- discussion autour d'un domaine de connaissance.

Le système doit prévoir une modération des contenus hors sujet.

## 8.3 Détail d'une publication

`/community/posts/:postId`

Contenu :

- auteur ;
- contenu ;
- médias/ressources ;
- réactions ;
- commentaires ;
- réponses ;
- signalement.

## 8.4 Profil communautaire

Le profil de chaque utilisateur peut exposer son activité communautaire selon les règles de confidentialité.

---

# 9. Mentors

**Route :**
`/mentors`

## 9.1 Découverte

- recherche ;
- catégories ;
- domaines ;
- disponibilité ;
- informations publiques ;
- tarifs lorsque pertinent.

## 9.2 Profil mentor

`/mentors/:mentorId`

Afficher :

- identité ;
- présentation ;
- domaines ;
- expérience ;
- cours ;
- avis si le système les utilise ;
- disponibilité ;
- réservation.

## 9.3 Réservation

`/mentors/:mentorId/book`

Étapes :

1. choix du service ;
2. choix du créneau ;
3. confirmation ;
4. paiement ;
5. réservation confirmée.

---

# 10. Sessions de mentorat

`/mentoring`

Contenu :

- prochaines sessions ;
- sessions passées ;
- réservations ;
- statut ;
- accès à la session lorsque disponible.

---

# 11. Progression

**Route :**
`/progress`

Afficher :

- cours commencés ;
- cours terminés ;
- progression ;
- quiz ;
- certificats obtenus ;
- activité d'apprentissage ;
- objectifs si activés.

---

# 12. Wallet / paiements

**Route :**
`/wallet`

Afficher selon le rôle et les permissions :

- solde ;
- transactions ;
- paiements ;
- achats ;
- remboursements ;
- commissions/revenus pour les profils concernés.

Routes possibles :

- `/wallet`
- `/wallet/transactions`
- `/wallet/transactions/:transactionId`

---

# 13. Notifications

`/notifications`

Types :

- progression ;
- quiz ;
- certification ;
- réservation ;
- mentorat ;
- communauté ;
- système ;
- paiement.

---

# 14. Profil

**Route :**
`/profile`

Sections :

- informations personnelles ;
- avatar ;
- bio ;
- domaines/intérêts ;
- progression ;
- certificats ;
- activité communautaire ;
- paramètres.

## 14.1 Profil public

`/users/:userId`

Le profil public doit respecter les permissions de visibilité.

---

# 15. Paramètres

`/settings`

Sous-sections :

- compte ;
- sécurité ;
- notifications ;
- confidentialité ;
- préférences ;
- paiements ;
- déconnexion.

---

# 16. Navigation responsive inspirée de Discord

## Mobile

Priorité :

```text
┌──────────────────────┐
│ Header / contexte    │
├──────────────────────┤
│                      │
│   Contenu principal  │
│                      │
│                      │
├──────────────────────┤
│ Navigation principale│
└──────────────────────┘
```

La navigation doit permettre un accès rapide aux espaces principaux sans surcharger l'écran.

## Tablette

Possibilité d'avoir :

```text
┌──────────┬──────────────────────┐
│ Sidebar  │ Contenu principal    │
│ compacte │                      │
│          │                      │
└──────────┴──────────────────────┘
```

## Desktop

Structure cible :

```text
┌──────────────┬──────────────────────────┬──────────────┐
│ Navigation   │ Contenu principal        │ Contextuel   │
│ persistante  │                          │              │
│              │                          │              │
└──────────────┴──────────────────────────┴──────────────┘
```

Le panneau contextuel est optionnel et ne doit pas réduire inutilement la zone de contenu.

---

# 17. Écrans transversaux

Prévoir également :

- états de chargement ;
- états vides ;
- erreurs ;
- accès refusé ;
- contenu supprimé ;
- contenu signalé ;
- confirmation d'action ;
- modales ;
- bottom sheets mobile ;
- drawers ;
- recherche globale.

---

# 18. Assets et références design

Les assets graphiques ne doivent pas être codés comme des éléments arbitraires.

Prévoir un espace d'assets :

```text
/assets
  /brand
  /icons
  /images
  /certificates
  /illustrations
```

Le logo SCHOOL ON fourni par le produit fait partie des assets officiels.

Les maquettes Figma servent de référence visuelle pour :

- layout ;
- spacing ;
- typographie ;
- couleurs ;
- composants ;
- responsive ;
- états des écrans.

---

# 19. Règle d'implémentation frontend

Chaque écran doit être relié à :

1. une route ;
2. un rôle/permission si nécessaire ;
3. un état de chargement ;
4. un état vide ;
5. un état d'erreur ;
6. les actions disponibles ;
7. les API nécessaires ;
8. les composants responsive.

Le `screen-map.md` décrit **où l'utilisateur va et ce qu'il voit**.

Il ne doit pas devenir le document principal des règles métier détaillées.
