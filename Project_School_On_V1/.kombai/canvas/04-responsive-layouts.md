# SCHOOL ON --- Responsive Layouts

## 1. Principle

Concevoir d'abord une structure qui reste compréhensible sur petit
écran, puis enrichir l'espace disponible sur tablette et desktop.

## 2. Mobile

Priorités :

-   navigation simple
-   une action principale par écran
-   cartes empilées
-   formulaires pleine largeur
-   quiz centré sur une question
-   lecture de cours sans distraction
-   boutons facilement utilisables au doigt

## 3. Tablet

Permettre :

-   deux colonnes lorsque le contenu le justifie
-   sidebar compacte ou navigation adaptée
-   grilles de cours
-   aperçu + contenu
-   tables simplifiées

## 4. Desktop

Permettre :

-   sidebar persistante
-   grilles multi-colonnes
-   panneaux secondaires
-   tables complètes
-   dashboard avec plusieurs blocs

## 5. Learning layout

### Desktop

``` text
┌────────────┬──────────────────────────┬─────────────┐
│ Course     │ Contenu du chapitre      │ Progression │
│ navigation │                          │ / ressources│
└────────────┴──────────────────────────┴─────────────┘
```

### Mobile

``` text
┌──────────────────────┐
│ Course / chapitre    │
├──────────────────────┤
│ Contenu              │
│                      │
├──────────────────────┤
│ Progression          │
├──────────────────────┤
│ Continuer            │
└──────────────────────┘
```

## 6. Quiz layout

Le quiz doit rester concentré :

``` text
Question
    ↓
Réponses
    ↓
Feedback éventuel
    ↓
Progression
    ↓
Suivant
```

Éviter de placer des informations secondaires qui détournent
l'attention.

## 7. Admin layout

Sur mobile :

-   transformer les tableaux en cartes ou vues scrollables
-   garder les informations critiques visibles
-   déplacer les actions secondaires dans un menu

Sur desktop :

-   utiliser les tableaux lorsque la comparaison de données est utile

## 8. Mentor profile

Desktop :

``` text
Avatar + identité
      ↓
Bio / expertise
      ↓
Cours
      ↓
Disponibilités
      ↓
Réserver
```

Mobile : empiler les sections avec l'action de réservation toujours
facilement accessible.

## 9. Certificate preview

Le certificat doit conserver son ratio et sa lisibilité.

Sur mobile :

-   aperçu redimensionné
-   informations essentielles visibles
-   action Télécharger / Vérifier clairement accessible

## 10. Forms

Les formulaires complexes doivent être découpés en sections.

Éviter les longues pages sans repères.

Utiliser :

-   labels persistants
-   aide contextuelle
-   validation claire
-   erreurs proches du champ
-   résumé avant soumission lorsque nécessaire
