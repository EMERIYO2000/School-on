# SCHOOL ON — Product Map

> **Document:** `product-map.md`  
> **Purpose:** définir les fonctionnalités, règles produit, rôles, relations entre modules et comportements attendus de SCHOOL ON.  
> **Statut:** base produit à utiliser conjointement avec le `screen-map.md` et le futur design Figma.

---

# 1. Vision produit

SCHOOL ON est une plateforme éducative qui combine :

- apprentissage ;
- cours ;
- quiz ;
- progression ;
- certification ;
- communauté éducative ;
- mentorat ;
- réservation ;
- paiement ;
- profils.

L'objectif est de ne pas traiter ces modules comme des produits indépendants, mais comme des éléments d'un même parcours.

```text
Découvrir
   ↓
Apprendre
   ↓
Pratiquer / Quiz
   ↓
Progresser
   ↓
Terminer
   ↓
Être certifié
   ↓
Partager / participer à la communauté
   ↓
Approfondir avec un mentor
```

---

# 2. Utilisateurs et rôles

## 2.1 Utilisateur

L'utilisateur standard peut notamment :

- créer un compte ;
- suivre des cours ;
- faire des quiz ;
- obtenir des certificats ;
- participer à la communauté ;
- consulter des mentors ;
- réserver des services selon les conditions ;
- gérer son profil ;
- gérer ses paiements.

## 2.2 Mentor

Le mentor possède les fonctionnalités d'un utilisateur auxquelles s'ajoutent les fonctionnalités liées à son activité :

- profil mentor ;
- création/gestion de contenu selon permissions ;
- gestion des cours attribués ;
- disponibilité ;
- réservations ;
- sessions ;
- suivi des apprenants lorsque prévu ;
- revenus/transactions lorsque prévu ;
- participation à la communauté.

## 2.3 Admin

L'admin gère notamment :

- utilisateurs ;
- mentors ;
- cours ;
- quiz ;
- catégories ;
- certifications ;
- communauté ;
- modération ;
- transactions ;
- paramètres globaux.

Les permissions doivent être contrôlées côté backend et pas uniquement dans l'interface.

---

# 3. Architecture fonctionnelle

```text
                         SCHOOL ON
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
   LEARNING             COMMUNITY            MENTORING
       │                    │                    │
   Courses              Posts                Mentors
   Modules              Comments             Booking
   Quiz                 Reactions            Sessions
   Progression          Reports              Availability
   Certification        Moderation
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    WALLET / PAYMENTS
                            │
                         PROFILS
```

---

# 4. Learning System

## 4.1 Cours

Un cours possède notamment :

- titre ;
- description ;
- auteur/mentor ;
- catégorie ;
- niveau ;
- modules ;
- contenu ;
- ressources ;
- prix si applicable ;
- statut de publication ;
- conditions de complétion.

## 4.2 Modules

Un cours est composé de modules/étapes d'apprentissage.

Le système doit pouvoir suivre :

- module consulté ;
- module terminé ;
- progression ;
- ordre des modules si imposé.

## 4.3 Progression

La progression doit être persistante côté backend.

Exemples :

```text
CourseProgress
 ├── user
 ├── course
 ├── percentage
 ├── completed_modules
 ├── status
 └── updated_at
```

La progression doit être cohérente avec les règles de complétion.

---

# 5. Quiz Engine

Les quiz sont intégrés au système d'apprentissage.

Le créateur définit :

- questions ;
- réponses ;
- bonne(s) réponse(s) ;
- points ;
- règles d'évaluation ;
- éventuellement seuil de réussite.

Types supportés selon le moteur :

- choix unique ;
- choix multiple ;
- autres modèles définis par le produit.

Le backend est responsable de la validation des réponses et du calcul du résultat.

---

# 6. Certification

La certification est une conséquence de la réussite/complétion définie par les règles du cours.

## 6.1 Conditions

Le système doit vérifier les conditions configurées :

- progression requise ;
- modules obligatoires ;
- quiz requis ;
- score minimum lorsque configuré ;
- autres conditions éventuelles.

## 6.2 Génération

Lorsque les conditions sont remplies :

```text
Course completed
      ↓
Eligibility check
      ↓
Certificate generation
      ↓
Mentor signature
      ↓
Certificate available
```

Le certificat doit être associé à :

- utilisateur ;
- cours ;
- mentor ;
- date ;
- identifiant unique ;
- signatures ;
- statut.

## 6.3 Modèle visuel

Le produit/design fournira un **modèle de certificat**.

Le modèle doit être traité comme une référence visuelle officielle et non comme une simple image décorative.

Le moteur de génération doit pouvoir injecter les données dynamiques dans le modèle.

---

# 7. Community / Forum

## 7.1 Définition

La Communauté est un **espace de publications éducatives**, inspiré dans son fonctionnement social de plateformes comme Facebook/Discord, mais spécialisé dans l'éducation.

Ce n'est pas un espace de discussion générale.

La communauté est visible et accessible dans l'expérience de **tous les profils**, pas uniquement des apprenants.

```text
Utilisateur ─┐
Mentor ──────┼──→ COMMUNITY
Admin ───────┘
```

Les droits d'action peuvent néanmoins varier selon le rôle.

---

## 7.2 Publications

Un utilisateur autorisé peut créer un post comprenant, selon les règles :

- texte ;
- image ;
- document ;
- ressource ;
- lien ;
- catégorie ;
- éventuellement d'autres médias.

Chaque post doit appartenir à un contexte éducatif.

Exemples :

- question pédagogique ;
- explication ;
- ressource ;
- conseil ;
- retour d'expérience d'apprentissage ;
- discussion sur une discipline ;
- aide à la compréhension d'un concept.

---

## 7.3 Restrictions de contenu

La communauté doit empêcher ou limiter les publications :

- sans rapport avec l'éducation ;
- purement promotionnelles selon les règles ;
- spam ;
- contenu abusif ;
- contenu illégal ;
- contenu destiné à détourner la plateforme de son objectif ;
- autres catégories interdites par les règles de modération.

Le système doit prévoir :

- signalement ;
- modération ;
- suppression/masquage ;
- statut de publication ;
- historique d'actions lorsque nécessaire.

---

## 7.4 Modèle fonctionnel

```text
CommunityPost
 ├── author
 ├── category
 ├── content
 ├── attachments
 ├── status
 ├── created_at
 └── updated_at

CommunityPost
 ├── Reactions
 ├── Comments
 │    └── Replies
 └── Reports
```

---

# 8. Catégories communautaires

Le système doit permettre d'organiser les publications par domaines.

Exemples :

- programmation ;
- design ;
- mathématiques ;
- sciences ;
- langues ;
- business ;
- intelligence artificielle ;
- culture ;
- carrière/orientation ;
- études/examens ;
- questions/entraide.

La liste définitive doit être administrable.

---

# 9. Mentorat

## 9.1 Découverte

L'utilisateur peut :

- rechercher un mentor ;
- consulter son profil ;
- voir ses domaines ;
- consulter ses services ;
- voir ses disponibilités lorsque disponibles.

## 9.2 Réservation

Flux :

```text
Choisir mentor
      ↓
Choisir service
      ↓
Choisir créneau
      ↓
Confirmer
      ↓
Paiement
      ↓
Réservation
      ↓
Session
```

Chaque étape doit avoir un statut persistant côté backend.

---

# 10. Paiement et Wallet

Le paiement doit être intégré aux fonctionnalités qui nécessitent une transaction :

- achat de cours ;
- réservation de mentor ;
- autres services payants.

Le système doit gérer :

- transaction ;
- montant ;
- devise ;
- statut ;
- référence ;
- utilisateur ;
- objet payé ;
- commission lorsque prévue ;
- remboursement lorsque prévu.

Les tests peuvent utiliser un provider simulé/fake provider avant l'intégration de vrais paiements.

---

# 11. Profils

## 11.1 Profil utilisateur

Le profil regroupe notamment :

- identité ;
- photo/avatar ;
- bio ;
- domaines ;
- progression ;
- certificats ;
- activité communautaire selon confidentialité.

## 11.2 Profil mentor

Le profil mentor ajoute :

- présentation professionnelle ;
- domaines d'expertise ;
- cours ;
- services ;
- disponibilité ;
- informations nécessaires au mentorat.

## 11.3 Communauté dans les profils

La communauté ne doit pas être liée uniquement au profil apprenant.

Tous les profils pertinents peuvent avoir une présence communautaire.

---

# 12. Notifications

Les notifications peuvent concerner :

- cours ;
- quiz ;
- progression ;
- certification ;
- mentor ;
- réservation ;
- paiement ;
- communauté ;
- modération ;
- système.

Le système doit éviter les notifications inutiles et permettre leur gestion par préférences.

---

# 13. Recherche

La recherche globale doit pouvoir évoluer pour couvrir :

- cours ;
- mentors ;
- publications ;
- utilisateurs/profils selon permissions ;
- catégories.

Chaque domaine peut également avoir sa recherche spécifique.

---

# 14. Modération

La modération est particulièrement importante pour la Communauté.

## 14.1 Signalement

Un utilisateur peut signaler :

- publication ;
- commentaire ;
- profil lorsque prévu.

Le signalement contient :

- objet ;
- motif ;
- auteur du signalement ;
- date ;
- statut.

## 14.2 Action de modération

L'administration peut :

- examiner ;
- masquer ;
- supprimer ;
- restaurer ;
- sanctionner selon les règles ;
- clôturer un signalement.

---

# 15. Design System et responsive

L'application doit être conçue **mobile-first** et s'adapter à :

- mobile ;
- tablette ;
- desktop.

L'expérience mobile peut s'inspirer de **Discord** pour :

- organisation en espaces ;
- navigation compacte ;
- sidebar/drawer ;
- hiérarchisation des sections ;
- accès rapide aux conversations/espaces.

Il ne s'agit pas de copier l'interface Discord.

Le comportement responsive est décrit dans `screen-map.md`.

---

# 16. Assets

Les assets officiels doivent être centralisés.

```text
Brand
 ├── Logo SCHOOL ON
 ├── Icons
 └── Brand assets

Content
 ├── Images
 ├── Illustrations
 └── Documents

Certification
 └── Certificate template
```

Le logo est déjà fourni.

Le modèle de certificat sera fourni séparément par le produit/design.

---

# 17. Figma comme source de vérité visuelle

Un fichier/design Figma sera fourni comme référence pour :

- identité visuelle ;
- écrans ;
- composants ;
- responsive ;
- états ;
- spacing ;
- typographie ;
- couleurs ;
- interactions ;
- composants réutilisables.

Le Figma ne remplace pas les règles produit.

```text
PRODUCT MAP
    ↓
ce que le produit doit faire

SCREEN MAP
    ↓
où et comment l'utilisateur accède aux fonctionnalités

FIGMA
    ↓
à quoi l'interface doit ressembler
```

---

# 18. Relation entre les documents

Les trois documents doivent rester complémentaires.

| Document | Question à laquelle il répond |
|---|---|
| `product-map.md` | Qu'est-ce que SCHOOL ON fait ? |
| `screen-map.md` | Où l'utilisateur fait-il ces actions ? |
| `Figma` | À quoi cela ressemble-t-il ? |

---

# 19. Règle de cohérence

Une fonctionnalité ne doit pas être ajoutée uniquement au frontend.

Pour chaque fonctionnalité :

```text
Product requirement
      ↓
Business rules
      ↓
Backend / API / DB
      ↓
Screen map
      ↓
UI / Figma
      ↓
Frontend
      ↓
Tests
```

Le backend reste l'autorité pour les règles métier sensibles :

- permissions ;
- progression ;
- quiz ;
- certification ;
- réservation ;
- paiement ;
- modération.

---

# 20. Hors périmètre actuel

Les éléments suivants peuvent être ajoutés dans de futurs documents ou versions :

- compte parent ;
- fonctionnalités sociales généralistes ;
- fonctionnalités non éducatives ;
- nouveaux rôles non validés ;
- fonctionnalités avancées de marketplace.

Ils ne doivent pas être ajoutés au produit simplement parce qu'ils existent dans d'autres réseaux sociaux.
