# SCHOOL ON --- Component System

## 1. Foundations

### Button

Variants :

-   Primary
-   Secondary
-   Outline
-   Ghost
-   Destructive
-   Link

States :

-   Default
-   Hover
-   Pressed
-   Focus
-   Disabled
-   Loading

### Input

Types :

-   text
-   email
-   password
-   number
-   search
-   textarea
-   select
-   date/time

States :

-   Default
-   Focus
-   Filled
-   Error
-   Disabled
-   Success

------------------------------------------------------------------------

## 2. Navigation

-   Sidebar
-   Top bar
-   Mobile navigation
-   Breadcrumb
-   Tabs
-   Pagination

------------------------------------------------------------------------

## 3. Content

-   Card
-   Course card
-   Mentor card
-   Certificate card
-   Stat card
-   Progress bar
-   Badge
-   Avatar
-   Empty state

------------------------------------------------------------------------

## 4. Learning

### Course card

Doit pouvoir afficher :

-   image
-   titre
-   mentor
-   niveau
-   progression
-   durée
-   statut

### Course detail

Sections possibles :

-   présentation
-   objectifs
-   contenu
-   mentor
-   progression
-   certification
-   action principale

### Learning player

Doit donner la priorité au contenu.

------------------------------------------------------------------------

## 5. Quiz

Composants :

-   Quiz header
-   Progress indicator
-   Question
-   Answer option
-   Multi-select option
-   Navigation
-   Result summary
-   Explanation
-   Retry / continue

Le système doit supporter plusieurs modèles de questions sans changer
l'identité visuelle globale.

------------------------------------------------------------------------

## 6. Mentor

### Mentor card

Afficher :

-   avatar
-   nom
-   domaine
-   statut de vérification
-   résumé
-   disponibilité
-   action

### Mentor profile

Sections :

-   identité publique
-   expertise
-   présentation
-   cours
-   disponibilités
-   réservation

Les données privées de vérification ne doivent pas apparaître.

------------------------------------------------------------------------

## 7. Booking

Composants :

-   date picker
-   time slot
-   session summary
-   booking status
-   confirmation
-   cancellation
-   session completion

------------------------------------------------------------------------

## 8. Certification

### Certificate card

Afficher :

-   titre du cours
-   bénéficiaire
-   date
-   statut
-   identifiant du certificat
-   action de consultation

### Certificate view

Le certificat doit avoir une présentation officielle et stable.

Actions :

-   consulter
-   télécharger
-   vérifier

------------------------------------------------------------------------

## 9. Feedback

-   Toast
-   Alert
-   Inline error
-   Success message
-   Confirmation dialog
-   Skeleton
-   Spinner

------------------------------------------------------------------------

## 10. Tables

Tables utilisées principalement dans l'espace mentor/admin.

Sur mobile :

-   cartes
-   scroll horizontal contrôlé
-   colonnes prioritaires

Ne jamais sacrifier la lisibilité pour conserver une table desktop sur
petit écran.
