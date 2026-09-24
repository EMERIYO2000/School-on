# SCHOOL ON — Learning & Quiz Engine

## Spécification fonctionnelle et architecture backend

> **Objectif du document :** fournir au développeur backend une spécification claire pour intégrer le système de création de cours, chapitres, contenus multimédias, quiz, Quiz Game, Quiz Training, questions des apprenants, correction automatique et historique des résultats.

---

# 1. Vision générale

SCHOOL ON ne doit pas considérer un cours ou un quiz comme un simple formulaire statique.

Le système doit fonctionner comme un **Learning & Assessment Engine** permettant à un **Mentor** ou à un **Admin** de créer des contenus pédagogiques structurés.

Un cours peut contenir plusieurs chapitres. Chaque chapitre peut contenir plusieurs types de contenus et éventuellement un quiz.

En parallèle, SCHOOL ON possède un moteur de quiz commun utilisé par :

- les quiz intégrés aux cours ;
- le **Quiz Game** ;
- le **Quiz Training** ;
- les préparations aux examens d'État ;
- plus tard, d'autres formes d'évaluation.

Le principe fondamental est :

> **Le concepteur définit les réponses correctes au moment de la création. Le système corrige automatiquement les tentatives des apprenants.**

Aucune intervention humaine ne doit être nécessaire pour valider un quiz utilisant les types de questions automatisables prévus dans la V1.

---

# 2. Acteurs

## 2.1. Apprenant

L'apprenant peut :

- consulter les cours publiés ;
- parcourir les chapitres ;
- regarder les vidéos ;
- consulter les images et documents ;
- répondre aux quiz ;
- poser une question à la fin d'un chapitre ;
- consulter les réponses du mentor ;
- participer au Quiz Game ;
- faire des Quiz Training ;
- consulter ses scores ;
- consulter son historique ;
- suivre sa progression.

## 2.2. Mentor

Le mentor peut, selon ses permissions :

- créer un cours ;
- ajouter des chapitres ;
- ajouter du contenu dans les chapitres ;
- ajouter des images ;
- ajouter des vidéos ;
- ajouter des documents ;
- créer des quiz ;
- créer des questions ;
- définir les bonnes réponses ;
- définir les points ;
- définir une explication de correction ;
- consulter les questions posées par les apprenants sur ses chapitres ;
- répondre aux apprenants ;
- soumettre son contenu à validation/publication.

## 2.3. Admin

L'Admin possède les capacités du mentor concernant la création de contenu, avec des permissions supplémentaires :

- créer des cours ;
- créer des quiz ;
- créer des Quiz Game ;
- créer des Quiz Training ;
- créer des contenus de préparation aux examens d'État ;
- modifier/supprimer les contenus selon ses permissions ;
- valider et publier les contenus ;
- gérer les catégories, matières, niveaux et années ;
- gérer les contenus créés par les mentors.

---

# 3. Architecture générale

Le système doit être pensé autour de deux moteurs principaux :

```text
SCHOOL ON
│
├── LEARNING ENGINE
│   │
│   ├── Courses
│   │   ├── Chapters
│   │   │   ├── Content Blocks
│   │   │   │   ├── Text
│   │   │   │   ├── Image
│   │   │   │   ├── Video
│   │   │   │   ├── Document
│   │   │   │   └── Code / Resource
│   │   │   │
│   │   │   ├── Chapter Quiz
│   │   │   └── Learner Questions
│   │   │
│   │   └── Final Quiz
│   │
│   └── Learning Progress
│
└── ASSESSMENT / QUIZ ENGINE
    │
    ├── Quiz Game
    ├── Quiz Training
    ├── Exam-State Preparation
    └── Question Engine
        ├── Single Choice
        ├── Multiple Choice
        ├── True / False
        └── Numeric / Calculated Answer
```

Le point important est que **Quiz Game et Quiz Training utilisent le même moteur de questions**.

Il ne faut donc pas créer deux systèmes de correction différents.

---

# 4. Système de cours

## 4.1. Informations générales du cours

Lorsqu'un mentor/admin crée un cours, il commence par les informations générales.

### Champs recommandés

- `title`
- `summary`
- `description`
- `category`
- `level`
- `learning_objectives`
- `cover_image`
- `estimated_duration`
- `price`
- `creator`
- `status`
- `created_at`
- `updated_at`

### Exemple

```text
Titre :
Introduction à JavaScript

Résumé :
Découvrez les bases du langage JavaScript...

Description :
Dans ce cours...

Niveau :
Débutant

Durée estimée :
6 heures

Prix :
10 000 FBU

Image :
javascript-cover.jpg
```

---

# 5. Système de chapitres

Un cours est composé de plusieurs chapitres.

```text
Course
│
├── Chapter 1
├── Chapter 2
├── Chapter 3
└── Chapter 4
```

Le créateur doit pouvoir utiliser :

> **+ Ajouter un chapitre**

Chaque chapitre possède au minimum :

- `course`
- `title`
- `summary`
- `description`
- `order`
- `created_at`
- `updated_at`

Le champ `order` est important pour conserver l'ordre pédagogique.

Exemple :

```text
1 — Introduction
2 — Variables
3 — Conditions
4 — Boucles
5 — Fonctions
```

---

# 6. Contenu dynamique des chapitres

Le mentor ne doit pas être limité à quelques champs fixes.

Chaque chapitre doit pouvoir recevoir plusieurs **Content Blocks**.

Exemple :

```text
Chapitre 2 — Les variables

Résumé
    ↓
Texte
    ↓
Image
    ↓
Vidéo
    ↓
Texte
    ↓
Exemple de code
    ↓
Document PDF
    ↓
Quiz
```

Le bouton principal peut être :

> **+ Ajouter un contenu**

Puis le créateur choisit le type :

- Texte
- Image
- Vidéo
- Document
- Code
- Ressource externe

## 6.1. Content Block

Structure logique :

```text
ContentBlock
├── chapter
├── type
├── title
├── content
├── file
├── url
├── order
├── created_at
└── updated_at
```

Tous les champs ne sont pas obligatoires selon le type.

Exemple :

### Type TEXT

```text
title
content
order
```

### Type IMAGE

```text
title
file
caption
order
```

### Type VIDEO

```text
title
file / url
description
duration
order
```

### Type DOCUMENT

```text
title
file
description
order
```

### Type CODE

```text
title
language
content
order
```

---

# 7. Quiz intégré à un chapitre

Un chapitre peut avoir un quiz.

Exemple :

```text
Chapitre 3
│
├── Contenu
├── Vidéo
├── Exemple
├── Quiz du chapitre
└── Questions des apprenants
```

Le quiz peut servir à vérifier la compréhension du chapitre.

Il doit utiliser le même `Question Engine` que les autres quiz.

---

# 8. Questions des apprenants

À la fin de chaque chapitre, l'apprenant doit pouvoir poser une question.

Interface :

```text
Vous avez une question sur ce chapitre ?

[ Écrivez votre question ici... ]

[ Poser ma question ]
```

La question doit être liée à :

- l'apprenant ;
- le cours ;
- le chapitre ;
- éventuellement un Content Block ;
- la date ;
- le statut.

Structure logique :

```text
LearnerQuestion
├── learner
├── course
├── chapter
├── content_block (optionnel)
├── question
├── answer
├── status
├── created_at
└── answered_at
```

### Statuts possibles

```text
PENDING
ANSWERED
ARCHIVED
```

Le mentor peut voir :

> **3 questions en attente**

et répondre.

L'apprenant pourra ensuite voir :

```text
Ma question :
Pourquoi utilise-t-on let ?

Réponse du mentor :
...
```

---

# 9. Le Question Engine

Le système de questions est le cœur du moteur d'évaluation.

Une question doit être indépendante du contexte dans lequel elle est utilisée.

Elle peut être associée à :

- un quiz de cours ;
- un Quiz Game ;
- un Quiz Training ;
- une préparation d'examen ;
- plus tard, d'autres systèmes.

Structure logique :

```text
Question
├── quiz
├── text
├── type
├── points
├── explanation
├── order
├── created_by
├── created_at
└── updated_at
```

---

# 10. Types de questions V1

## 10.1. Choix unique

Une seule réponse correcte.

Exemple :

```text
Quelle est la capitale du Burundi ?

A. Kigali
B. Bujumbura
C. Nairobi
D. Kampala
```

Le concepteur définit :

```text
correct_answer = Bujumbura
```

Le système vérifie automatiquement la réponse de l'apprenant.

---

## 10.2. Choix multiple

Plusieurs réponses peuvent être correctes.

Exemple :

```text
Lesquels sont des langages de programmation ?

☑ Python
☑ JavaScript
☐ HTML
☐ Photoshop
```

Le concepteur définit :

```text
correct_answers = [
    Python,
    JavaScript
]
```

Le système doit comparer l'ensemble des réponses.

Il faut décider clairement si le mode de correction est :

```text
Tout ou rien
```

pour la V1.

Recommandation V1 :

> Une réponse n'est considérée correcte que si l'ensemble des bonnes réponses est sélectionné et qu'aucune mauvaise réponse n'est sélectionnée.

Cela simplifie le calcul.

---

## 10.3. Vrai / Faux

Exemple :

```text
JavaScript est un langage de programmation.

A. Vrai
B. Faux
```

Le concepteur définit :

```text
correct_answer = Vrai
```

Correction automatique.

---

## 10.4. Réponse numérique / calcul

Pour les questions mathématiques ou scientifiques.

Exemple :

```text
Quel est le résultat de 15 × 4 ?
```

Réponse correcte :

```text
60
```

Le système peut comparer la réponse numérique.

Pour une future version, prévoir éventuellement :

- tolérance ;
- unités ;
- arrondis.

Mais la V1 peut rester simple.

---

# 11. Réponse explicative

Ce type est plus complexe.

Il peut être prévu dans l'architecture mais ne doit pas être obligatoire pour la première version.

```text
FREE_TEXT
```

Le concepteur peut définir une réponse attendue, mais la correction automatique d'une réponse rédigée nécessite une logique supplémentaire.

### V1 recommandée

Ne pas intégrer ce type dans le système de correction automatique.

### V2 possible

Utiliser une IA pour proposer une note à partir de :

- la question ;
- les critères ;
- la réponse attendue ;
- la réponse de l'apprenant ;
- le barème.

Le mentor/admin pourrait ensuite valider ou modifier la note.

---

# 12. Création d'une question

Le formulaire de création doit être dynamique.

Exemple :

```text
Question

[ Quel est le rôle principal du processeur ? ]

Type

[ Choix unique ▼ ]
```

Si `Choix unique` :

```text
Réponse A : ...
Réponse B : ...
Réponse C : ...
Réponse D : ...

Bonne réponse :
[ B ]

Points :
[ 1 ]

Explication :
[ ... ]
```

Si `Choix multiple` :

```text
☐ Réponse A
☑ Réponse B
☑ Réponse C
☐ Réponse D
```

Si `Vrai/Faux` :

```text
Bonne réponse :
[ Vrai ]
```

Si `Numérique` :

```text
Réponse correcte :
[ 60 ]

Points :
[ 2 ]
```

Le backend doit donc valider les données selon le `question_type`.

---

# 13. Création de quiz

Le créateur peut :

1. créer un quiz ;
2. ajouter des informations ;
3. ajouter des questions ;
4. définir le type de chaque question ;
5. définir les réponses ;
6. définir les points ;
7. ajouter les explications ;
8. enregistrer ;
9. publier selon ses permissions.

Interface logique :

```text
Créer un quiz

Titre
Description
Type de quiz
Catégorie
Matière
Niveau
Durée
Nombre de questions
Image

Questions
────────────────────────
Question 1
Type
Réponses
Bonne réponse
Points
Explication

+ Ajouter une question

Question 2
...

[ Enregistrer ]
[ Soumettre ]
[ Publier ]
```

---

# 14. Quiz Game

Le **Quiz Game** est destiné à une expérience plus ludique.

Les quiz sont classés par :

- catégorie ;
- niveau ;
- difficulté ;
- éventuellement thème.

Exemples de catégories :

- Mathématiques
- Informatique
- Sciences
- Français
- Anglais
- Culture générale
- Logique
- etc.

Exemple :

```text
QUIZ GAME

Catégorie : Informatique
Niveau : Intermédiaire
Questions : 15
Durée : 5 minutes
Score maximum : 150
```

Le moteur :

1. récupère les questions ;
2. mélange éventuellement les questions ;
3. mélange les réponses ;
4. démarre le chronomètre ;
5. enregistre les réponses ;
6. vérifie les réponses ;
7. calcule le score ;
8. enregistre la tentative ;
9. affiche le résultat.

---

# 15. Quiz Training

Le **Quiz Training** est destiné à l'entraînement et à la préparation académique.

Il doit être organisé de manière plus précise.

Métadonnées recommandées :

```text
Quiz Training
├── category
├── subject
├── level
├── school_level
├── year
├── session
├── series
├── duration
└── type
```

Exemple :

```text
Examen d'État
    ↓
Mathématiques
    ↓
2025
    ↓
Algèbre
    ↓
Série 02
```

Ou :

```text
Français
    ↓
2026
    ├── Grammaire
    ├── Compréhension
    └── Littérature
```

---

# 16. Pourquoi conserver l'année ?

L'année permet de contextualiser les entraînements.

Exemple :

```text
Mathématiques — 2025
Mathématiques — 2024
Mathématiques — 2023
```

L'année ne doit cependant pas être la seule classification.

Un quiz peut également avoir :

- une catégorie ;
- une matière ;
- un niveau ;
- un thème ;
- une série ;
- un type d'examen.

Cela permettra de construire de meilleurs filtres.

---

# 17. Correction automatique

Le principe fondamental :

> Le concepteur définit les réponses correctes une seule fois. Le système utilise ensuite ces données pour toutes les tentatives.

Exemple :

```text
Question
    ↓
Réponse correcte enregistrée
    ↓
Apprenant répond
    ↓
Comparaison
    ↓
Correct / Incorrect
    ↓
Points
    ↓
Score final
```

Aucune validation humaine n'est nécessaire pour :

- choix unique ;
- choix multiple ;
- vrai/faux ;
- réponse numérique selon les règles de la V1.

---

# 18. Calcul du score

Chaque question possède un nombre de points.

Exemple :

```text
Question 1 → 1 point
Question 2 → 2 points
Question 3 → 1 point
Question 4 → 3 points
```

Le score maximum est :

```text
1 + 2 + 1 + 3 = 7
```

Si l'apprenant obtient 5 points :

```text
Score = 5 / 7
```

Pourcentage :

```text
(5 / 7) × 100 = 71,43 %
```

Le backend doit conserver le score brut et le pourcentage.

---

# 19. Chronomètre

Un quiz peut avoir une durée.

Exemple :

```text
Durée : 10 minutes
```

Le backend doit enregistrer :

- `started_at`
- `submitted_at`
- éventuellement `duration`

Le frontend affiche le chronomètre.

Important :

> Le backend doit être considéré comme l'autorité pour la limite de temps.

Il ne faut pas faire confiance uniquement au JavaScript du navigateur.

Si le temps est dépassé, le backend doit pouvoir refuser ou clôturer la tentative selon les règles du quiz.

---

# 20. Mélange des questions et réponses

Le système doit pouvoir mélanger :

### Questions

```text
Avant :
1 → 2 → 3 → 4 → 5

Après :
3 → 1 → 5 → 2 → 4
```

### Réponses

```text
Avant :
A. Python
B. JavaScript
C. Java
D. PHP

Après :
A. Java
B. PHP
C. Python
D. JavaScript
```

Le système doit toutefois conserver l'identité réelle de la bonne réponse en base.

Le mélange ne doit jamais modifier le corrigé.

---

# 21. Tentative d'un apprenant

Il faut distinguer le **Quiz** de la **Tentative**.

```text
Quiz
│
├── Question 1
├── Question 2
└── Question 3

Attempt
│
├── learner
├── quiz
├── started_at
├── submitted_at
├── score
├── percentage
└── status
```

Une même personne peut donc faire plusieurs tentatives si le quiz l'autorise.

---

# 22. Historique des résultats

L'apprenant doit pouvoir consulter :

```text
Mes résultats

Mathématiques — Série 02
84 %
19 septembre 2026

Informatique — Niveau intermédiaire
72 %
18 septembre 2026

Français — 2025
91 %
17 septembre 2026
```

Une tentative doit conserver au minimum :

- apprenant ;
- quiz ;
- date ;
- durée ;
- score ;
- pourcentage ;
- nombre de bonnes réponses ;
- nombre de mauvaises réponses ;
- statut.

---

# 23. Progression

Le système peut ensuite utiliser les tentatives pour produire :

```text
Mathématiques

Tentative 1 → 62 %
Tentative 2 → 71 %
Tentative 3 → 78 %
Tentative 4 → 84 %
```

Cela permettra plus tard de construire :

- progression par matière ;
- taux de réussite ;
- domaines faibles ;
- domaines forts ;
- recommandations de révision.

Ces fonctionnalités ne sont pas obligatoires pour la première version du moteur.

---

# 24. Modèles backend recommandés

La structure exacte dépendra de l'architecture Django/API du projet, mais conceptuellement les entités sont :

```text
User
│
├── Course
│   ├── Chapter
│   │   ├── ContentBlock
│   │   ├── Quiz
│   │   │   └── Question
│   │   │       └── Answer
│   │   └── LearnerQuestion
│   │
│   └── FinalQuiz
│
├── Quiz
│   └── Question
│       └── Answer
│
└── QuizAttempt
    └── AttemptAnswer
```

---

# 25. Structure conceptuelle des modèles

## Course

```text
id
creator
title
summary
description
category
level
learning_objectives
cover_image
estimated_duration
price
status
created_at
updated_at
```

## Chapter

```text
id
course
title
summary
description
order
created_at
updated_at
```

## ContentBlock

```text
id
chapter
type
title
text_content
file
url
language
caption
order
created_at
updated_at
```

Selon le type, certains champs seront utilisés ou ignorés.

---

## Quiz

```text
id
creator
title
description
quiz_type
category
subject
level
school_level
year
session
series
duration
status
course
chapter
created_at
updated_at
```

`quiz_type` peut contenir par exemple :

```text
COURSE
GAME
TRAINING
EXAM_PREP
```

Le système peut évoluer avec d'autres types plus tard.

---

## Question

```text
id
quiz
text
question_type
points
explanation
order
created_by
created_at
updated_at
```

`question_type` :

```text
SINGLE_CHOICE
MULTIPLE_CHOICE
TRUE_FALSE
NUMERIC
FREE_TEXT
```

`FREE_TEXT` peut être désactivé du système de correction automatique dans la V1.

---

## Answer

```text
id
question
text
is_correct
order
```

Pour `NUMERIC`, la structure peut évoluer vers un champ spécialisé.

---

## LearnerQuestion

```text
id
learner
course
chapter
content_block
question
answer
status
created_at
answered_at
```

---

## QuizAttempt

```text
id
quiz
learner
started_at
submitted_at
score
max_score
percentage
correct_answers
wrong_answers
status
```

---

## AttemptAnswer

```text
id
attempt
question
selected_answer
answer_text
is_correct
points_awarded
answered_at
```

Cette entité est importante pour conserver exactement ce que l'apprenant a répondu.

---

# 26. Statuts

## Course

```text
DRAFT
SUBMITTED
REVIEW
PUBLISHED
ARCHIVED
```

## Quiz

```text
DRAFT
SUBMITTED
REVIEW
PUBLISHED
ARCHIVED
```

## LearnerQuestion

```text
PENDING
ANSWERED
ARCHIVED
```

## QuizAttempt

```text
IN_PROGRESS
SUBMITTED
EXPIRED
```

---

# 27. Permissions

| Fonction                             |      Apprenant |         Mentor |          Admin |
| ------------------------------------ | -------------: | -------------: | -------------: |
| Consulter cours publiés              |             ✅ |             ✅ |             ✅ |
| Créer cours                          |             ❌ |             ✅ |             ✅ |
| Modifier son cours                   |             ❌ |             ✅ |             ✅ |
| Créer quiz                           |             ❌ |             ✅ |             ✅ |
| Créer questions                      |             ❌ |             ✅ |             ✅ |
| Définir réponses correctes           |             ❌ |             ✅ |             ✅ |
| Faire quiz                           |             ✅ | éventuellement | éventuellement |
| Voir ses résultats                   |             ✅ |             ✅ |             ✅ |
| Poser question sur chapitre          |             ✅ |             ❌ |             ❌ |
| Répondre aux questions               |             ❌ |             ✅ |             ✅ |
| Publier contenu                      | selon workflow | selon workflow |             ✅ |
| Modifier contenu d'un autre créateur |             ❌ |             ❌ |             ✅ |

---

# 28. API — organisation conceptuelle

L'API peut être organisée autour des ressources.

Exemple :

```text
/api/courses/
/api/courses/{id}/chapters/
/api/chapters/{id}/contents/
/api/chapters/{id}/questions/

/api/quizzes/
/api/quizzes/{id}/questions/
/api/questions/{id}/answers/

/api/quiz-attempts/
/api/quiz-attempts/{id}/submit/

/api/learner-questions/
/api/learner-questions/{id}/answer/
```

Les URLs exactes restent à adapter à l'architecture actuelle du backend.

---

# 29. Workflow de création d'un cours

```text
MENTOR / ADMIN
      ↓
Créer le cours
      ↓
Informations générales
      ↓
Créer chapitre 1
      ↓
Ajouter contenu
      ↓
Ajouter images / vidéos / documents
      ↓
Ajouter quiz du chapitre
      ↓
Définir questions + réponses
      ↓
Ajouter chapitre suivant
      ↓
...
      ↓
Enregistrer en brouillon
      ↓
Soumettre
      ↓
Validation si nécessaire
      ↓
PUBLICATION
```

---

# 30. Workflow d'un apprenant

```text
APPRENANT
    ↓
Ouvre le cours
    ↓
Chapitre 1
    ↓
Consulte le contenu
    ↓
Répond au quiz
    ↓
Pose éventuellement une question
    ↓
Chapitre 2
    ↓
...
    ↓
Termine le cours
    ↓
Résultat / progression
```

---

# 31. Workflow Quiz Game

```text
APPRENANT
    ↓
Quiz Game
    ↓
Choisit catégorie
    ↓
Choisit niveau
    ↓
Choisit quiz
    ↓
Démarrer
    ↓
Questions mélangées
    ↓
Chronomètre
    ↓
Réponses
    ↓
Soumission
    ↓
Correction automatique
    ↓
Score
    ↓
Historique
```

---

# 32. Workflow Quiz Training

```text
APPRENANT
    ↓
Quiz Training
    ↓
Choisit examen / niveau
    ↓
Choisit matière
    ↓
Choisit année
    ↓
Choisit série
    ↓
Lance l'entraînement
    ↓
Répond
    ↓
Correction automatique
    ↓
Résultat
    ↓
Correction détaillée
    ↓
Historique
```

---

# 33. Règles importantes pour le backend

## Règle 1 — Le frontend ne doit pas être l'autorité

Le frontend peut afficher le chronomètre et les résultats, mais le backend doit vérifier :

- l'utilisateur ;
- le quiz ;
- les questions ;
- les réponses ;
- le temps ;
- les points ;
- le score.

## Règle 2 — Ne jamais faire confiance au score envoyé par le client

Le frontend ne doit jamais envoyer :

```text
score = 90
```

et demander au serveur de l'enregistrer.

Le backend doit calculer :

```text
réponses utilisateur
        ↓
comparaison avec corrigé
        ↓
points
        ↓
score final
```

## Règle 3 — Le corrigé ne doit pas être exposé inutilement

Lorsque l'apprenant récupère les questions avant de répondre, l'API ne doit pas exposer directement :

```text
is_correct = true
```

Sinon l'utilisateur pourrait inspecter la réponse dans le navigateur.

Le corrigé doit rester côté serveur autant que possible.

## Règle 4 — Une tentative doit être traçable

Conserver les réponses données par l'apprenant permet de :

- montrer la correction ;
- calculer les statistiques ;
- consulter l'historique ;
- analyser les erreurs ;
- empêcher certaines incohérences.

---

# 34. MVP recommandé

Pour éviter de rendre le projet trop gros dès le départ, implémenter dans cet ordre.

## Phase 1 — Question Engine

- Question
- Answer
- Single Choice
- Multiple Choice
- True/False
- Numeric
- Points
- Explication
- Correction automatique

## Phase 1 — Quiz

- création de quiz ;
- ajout de questions ;
- durée ;
- mélange ;
- soumission ;
- calcul du score.

## Phase 1 — Attempts

- QuizAttempt ;
- AttemptAnswer ;
- historique ;
- correction détaillée.

## Phase 1 — Quiz Game

- catégories ;
- niveaux ;
- quiz publics ;
- expérience ludique.

## Phase 1 — Quiz Training

- matières ;
- niveaux scolaires ;
- années ;
- séries ;
- préparation aux examens d'État.

## Phase 1 — Course Builder

- cours ;
- chapitres ;
- Content Blocks ;
- images ;
- vidéos ;
- documents ;
- quiz de chapitre.

## Phase 1 — Questions des apprenants

- poser une question ;
- liste des questions ;
- réponse du mentor ;
- notifications éventuelles.

## Phase 2 — Fonctionnalités avancées

- statistiques ;
- progression ;
- recommandations ;
- analyse des erreurs ;
- IA pour les réponses explicatives ;
- génération assistée de questions.

---

# 35. Résumé de l'architecture finale

```text
                         SCHOOL ON
                             │
             ┌───────────────┴────────────────┐
             │                                │
       LEARNING ENGINE                  QUIZ ENGINE
             │                                │
          COURSES                         QUIZZES
             │                                │
         CHAPTERS                   ┌─────────┼─────────┐
             │                      │         │         │
       CONTENT BLOCKS            GAME     TRAINING   EXAM PREP
             │                      │         │         │
       ┌─────┼─────┐                └─────────┼─────────┘
       │     │     │                          │
     TEXT IMAGE VIDEO                   QUESTION ENGINE
       │     │     │                          │
       │     │     ├──────────────┐           │
       │     │     │              │           │
       │     │   DOCUMENT       QUIZ     ┌────┼───────────┐
       │     │                    │       │    │     │     │
       │     │                    │    SINGLE MULTI TRUE NUMERIC
       │     │                    │    CHOICE CHOICE FALSE
       │     │                    │
       │     │                    └─────────────┐
       │     │                                  │
       └─────┴──────────────┐             AUTOMATIC
                            │              GRADING
                    LEARNER QUESTIONS          │
                            │             SCORE / RESULT
                         MENTOR                  │
                         ANSWER              HISTORY
```

---

# 36. Principe fondamental à retenir

Le backend doit être construit autour de cette idée :

> **Le créateur construit le contenu et définit le corrigé. SCHOOL ON exécute, corrige, calcule et mémorise.**

Le mentor/admin n'a donc pas à corriger manuellement les quiz standards.

Il crée :

```text
Question
+
Réponses
+
Bonne réponse
+
Points
+
Explication
```

Puis le système s'occupe automatiquement de :

```text
Présentation
→ Réponse
→ Vérification
→ Correction
→ Score
→ Résultat
→ Historique
→ Progression
```

Cette architecture permet à SCHOOL ON de commencer simplement tout en restant extensible vers des fonctionnalités plus avancées comme l'analyse des performances, la personnalisation des entraînements et l'assistance IA.
