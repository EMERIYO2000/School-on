# SCHOOL ON — Vision, Sécurité, Expérience et Modèle économique

> **Une plateforme intelligente pour apprendre, enseigner et s'entraider**

## 1. Objectif de ce document

Ce document consolide les nouvelles réflexions autour de SCHOOL ON afin de transformer l'idée générale en une vision plus cohérente, réaliste et défendable.

Il répond notamment à huit questions :

1. Comment éviter que le système de mentorat soit détourné à des fins dangereuses ?
2. Quel problème réel SCHOOL ON résout-il face à YouTube et aux IA ?
3. Comment sécuriser le paiement d'un mentor jusqu'à la fin du cours ?
4. Comment réduire les risques d'imposteurs et créer un système de confiance ?
5. Comment construire un modèle économique viable ?
6. Comment intégrer efficacement les examens d'État et les tests de 9ème ?
7. Quel rôle concret donner à l'IA ?
8. Comment répondre aux trois critères d'évaluation : pertinence humaine et sociale, simplicité d'usage et robustesse technique ?

---

# 2. Positionnement de SCHOOL ON

SCHOOL ON ne doit pas être présenté simplement comme :

> « une plateforme avec des cours en ligne et de l'IA ».

Le projet cherche plutôt à réunir plusieurs éléments autour du parcours d'un apprenant :

**CONTENU + PRATIQUE + PERSONNE + COMMUNAUTÉ + PROGRESSION**

L'idée centrale est qu'un apprenant ne manque pas forcément de contenu. Il peut déjà trouver des vidéos, des documents ou demander une explication à une IA.

Le problème peut être l'absence de parcours clair et d'accompagnement.

SCHOOL ON cherche donc à permettre à un utilisateur de :

- trouver quoi apprendre ;
- apprendre avec des ressources structurées ;
- pratiquer avec des quiz et examens blancs ;
- demander de l'aide ;
- trouver un mentor lorsqu'un accompagnement humain est nécessaire ;
- suivre sa progression ;
- permettre, lorsque c'est pertinent, à un tuteur de suivre et financer le parcours d'un apprenant.

---

# 3. Le problème réel à résoudre

## 3.1. Le problème ne doit pas être « Internet n'a pas de contenu »

Aujourd'hui, un apprenant peut déjà utiliser :

- YouTube ;
- des moteurs de recherche ;
- des plateformes éducatives ;
- des assistants IA ;
- des PDF et documents en ligne.

SCHOOL ON ne doit donc pas essayer de gagner en disant simplement qu'il possède « plus de contenu ».

## 3.2. Le problème ciblé

Dans le contexte de Gitega, un apprenant qui rencontre une difficulté peut avoir accès à de nombreuses ressources sans forcément savoir :

- quelle ressource choisir ;
- dans quel ordre apprendre ;
- comment mesurer son niveau ;
- comment s'entraîner pour un examen ;
- à qui demander une aide humaine ;
- comment trouver un mentor de confiance ;
- comment suivre sa progression.

SCHOOL ON cherche à connecter ces besoins dans une même expérience.

## 3.3. Exemple concret

Une élève de 9ème prépare un examen et rencontre des difficultés en mathématiques.

Avec une recherche classique, elle peut trouver de nombreuses vidéos et documents.

Avec une IA, elle peut demander une explication.

Avec SCHOOL ON, l'objectif est de lui proposer un parcours :

1. identifier son niveau ;
2. réviser une notion ;
3. faire un exercice ;
4. passer un quiz ;
5. identifier ses lacunes ;
6. recevoir une recommandation ;
7. demander de l'aide à l'IA ;
8. trouver un mentor vérifié si l'accompagnement humain est nécessaire ;
9. mesurer sa progression ;
10. recommencer sur les notions où elle est encore faible.

La valeur de SCHOOL ON se trouve donc dans **l'orchestration du parcours**, pas uniquement dans la présence de contenu.

---

# 4. Le parcours central de SCHOOL ON

```text
                 APPRENANT
                     │
                     ▼
              Je veux apprendre
                     │
              ┌──────┴──────┐
              ▼             ▼
            COURS          QUIZ
              │             │
              └──────┬──────┘
                     ▼
              Difficulté détectée
                     │
               ┌─────┴─────┐
               ▼           ▼
              IA         MENTOR
               │           │
               └─────┬─────┘
                     ▼
                PROGRESSION
                     │
                     ▼
                 NOUVEAU QUIZ
```

Cette boucle doit devenir le fil conducteur de l'application.

---

# 5. Sécurité du système de mentorat

Le mentorat est une fonctionnalité à forte valeur, mais elle crée également des risques.

Un système permettant de réserver une personne et de partager une localisation peut être détourné.

SCHOOL ON doit donc appliquer le principe :

> **La localisation sert à faciliter un accompagnement, pas à permettre de localiser librement des personnes.**

## 5.1. Ne pas afficher l'adresse exacte publiquement

Un profil peut afficher :

- Gitega ;
- une zone approximative ;
- les domaines d'expertise ;
- les disponibilités.

L'adresse exacte ne doit pas être une information publique du profil.

## 5.2. Réservation

Le parcours peut être :

```text
Recherche du mentor
        ↓
Choix du domaine
        ↓
Choix du mode
(en ligne / présentiel)
        ↓
Choix date + durée
        ↓
Demande de réservation
        ↓
Acceptation du mentor
        ↓
Cours
        ↓
Confirmation
```

## 5.3. Privilégier les lieux sûrs

Pour une première rencontre physique, SCHOOL ON peut encourager :

- établissements scolaires ;
- bibliothèques ;
- centres partenaires ;
- lieux publics appropriés ;
- autres lieux validés.

Il faut éviter que le fonctionnement normal de la plateforme pousse automatiquement les utilisateurs vers des rencontres à domicile avec des inconnus.

## 5.4. Fonctionnalités de sécurité complémentaires

À prévoir progressivement :

- vérification des comptes ;
- signalement ;
- blocage ;
- historique des réservations ;
- système de réputation ;
- règles de conduite ;
- modération ;
- mécanisme de litige ;
- conservation des traces nécessaires aux opérations de sécurité.

---

# 6. Paiement sécurisé des mentors

Le modèle envisagé correspond à un système de paiement avec conservation temporaire des fonds, souvent appelé **escrow**.

## 6.1. Exemple

Prix du cours :

**5 000 FBU**

L'étudiant paie au moment de la réservation.

L'argent n'est pas immédiatement considéré comme acquis par le mentor.

Le système garde la transaction dans un état :

> **Paiement sécurisé**

## 6.2. Cycle de transaction

```text
ÉTUDIANT
   │
   │ 5 000 FBU
   ▼
SCHOOL ON / PRESTATAIRE DE PAIEMENT
   │
   ▼
Réservation acceptée
   │
   ▼
Cours réalisé
   │
   ├──────────────┐
   ▼              ▼
Étudiant       Mentor
confirme       confirme
   │              │
   └──────┬───────┘
          ▼
    Paiement libéré
          │
          ▼
        Mentor
```

## 6.3. États possibles

Une transaction peut utiliser des statuts tels que :

- `PENDING` — paiement en attente ;
- `PAID` — paiement reçu ;
- `BOOKING_CONFIRMED` — réservation confirmée ;
- `IN_PROGRESS` — cours en cours ;
- `COMPLETED` — cours terminé ;
- `RELEASED` — paiement libéré ;
- `DISPUTED` — litige ;
- `REFUNDED` — remboursement ;
- `FAILED` — paiement échoué ;
- `CANCELLED` — réservation annulée.

## 6.4. Si l'étudiant ne confirme pas

Il faut définir une règle automatique.

Exemple :

> Après la fin déclarée du cours, l'étudiant dispose d'un délai pour signaler un problème.

S'il ne signale rien pendant ce délai, le paiement peut être automatiquement libéré selon les règles du prestataire de paiement et les conditions de SCHOOL ON.

## 6.5. Si les deux déclarent des informations différentes

Exemple :

- Mentor : « cours terminé »
- Étudiant : « cours non réalisé »

La transaction passe en :

> **LITIGE**

SCHOOL ON doit alors disposer d'un processus de résolution.

---

# 7. Authentification et confiance des mentors

Un simple bouton « Devenir mentor » ne suffit pas.

Il faut construire plusieurs niveaux de confiance.

## 7.1. Niveau 1 — Utilisateur

Tout utilisateur peut créer un compte standard.

Il peut apprendre, participer à la communauté et utiliser les fonctions accessibles à son niveau.

## 7.2. Niveau 2 — Demande de profil professionnel

L'utilisateur demande à devenir mentor et fournit notamment :

- identité ;
- numéro de téléphone ;
- photo ;
- domaines de compétence ;
- niveau d'étude ;
- expérience ;
- formations ;
- certifications ou diplômes lorsque disponibles.

## 7.3. Niveau 3 — Identité vérifiée

Après vérification :

> ✓ Identité vérifiée

## 7.4. Niveau 4 — Mentor certifié

Après validation supplémentaire :

> 🏆 Mentor certifié SCHOOL ON

La certification doit correspondre à des critères clairement définis.

## 7.5. Réputation

Le badge ne doit pas être le seul indicateur.

Le profil peut également afficher :

- nombre de cours réalisés ;
- note moyenne ;
- taux de cours terminés ;
- ancienneté ;
- domaines enseignés ;
- nombre d'évaluations.

Exemple :

```text
Mentor vérifié
47 cours
4,8 ★
96 % de cours terminés
Mathématiques
```

## 7.6. Principe important

SCHOOL ON ne doit pas promettre qu'une vérification rend une personne « 100 % sûre ».

L'objectif est de **réduire les risques et augmenter la confiance**, grâce à plusieurs mécanismes combinés :

**Vérification + réputation + signalement + modération + sécurité des rencontres + paiement sécurisé.**

---

# 8. Modèle économique

SCHOOL ON peut évoluer vers plusieurs sources de revenus.

## 8.1. Commission sur le mentorat

Exemple :

Cours : 5 000 FBU

Commission SCHOOL ON : 10 %

Mentor : 4 500 FBU

SCHOOL ON : 500 FBU

Le pourcentage réel devra être déterminé selon les coûts du paiement, du fonctionnement et du marché.

## 8.2. Commission sur les formations

Un professionnel peut vendre une formation.

Exemple :

```text
Formation : 15 000 FBU
       ↓
Paiement
       ↓
SCHOOL ON
       ↓
Part reversée au créateur
       +
Commission SCHOOL ON
```

## 8.3. Abonnement Premium

### Gratuit

- cours gratuits ;
- communauté ;
- certains quiz ;
- fonctionnalités de base.

### Premium

Possibilités :

- contenu premium ;
- statistiques avancées ;
- parcours personnalisés ;
- fonctionnalités IA avancées ;
- fonctionnalités supplémentaires de préparation aux examens.

Les fonctionnalités exactes doivent être validées après observation des besoins réels.

## 8.4. Offre pour écoles et institutions

À moyen terme :

> **SCHOOL ON for Schools**

Une école pourrait utiliser SCHOOL ON pour :

- gérer ses apprenants ;
- organiser des cours ;
- créer des quiz ;
- suivre les progrès ;
- faciliter les échanges ;
- exploiter les outils pédagogiques.

---

# 9. SCHOOL ON EXAM

La préparation aux examens doit devenir une fonctionnalité identifiable.

## 9.1. Examens d'État

L'utilisateur choisit par exemple :

```text
Pays : Burundi
Niveau : 9ème
Matière : Mathématiques
```

Puis :

- exercices ;
- quiz ;
- examens blancs ;
- questions issues d'examens précédents lorsque leur utilisation est autorisée ;
- corrections ;
- explications ;
- statistiques.

## 9.2. Test de 9ème

Créer une expérience dédiée à ceux qui préparent leur test de 9ème.

Exemple :

> **Préparer mon examen**

→ choisir une matière  
→ faire un test  
→ recevoir un score  
→ voir les lacunes  
→ réviser  
→ refaire un test.

## 9.3. Boucle pédagogique

```text
TEST
 ↓
SCORE
 ↓
LACUNES
 ↓
COURS RECOMMANDÉ
 ↓
EXERCICES
 ↓
NOUVEAU TEST
 ↓
PROGRESSION
```

Cette boucle crée une vraie cohérence entre les fonctionnalités.

---

# 10. Rôle de l'intelligence artificielle

L'objectif ne doit pas être :

> « Mettre de l'IA parce que toutes les applications ont de l'IA. »

L'IA doit résoudre des problèmes précis.

## 10.1. Tuteur personnel

L'apprenant peut poser une question.

Exemple :

> « Je ne comprends pas cette équation. »

L'IA peut expliquer progressivement, proposer un exemple et demander à l'apprenant d'essayer.

## 10.2. Détection des lacunes

À partir des résultats aux quiz, le système peut identifier les domaines dans lesquels l'apprenant rencontre régulièrement des difficultés.

Exemple :

> « Tu réussis les équations simples mais tu rencontres davantage de difficultés avec les systèmes d'équations. »

## 10.3. Génération d'exercices

L'IA peut aider à générer des exercices adaptés :

> « Donne-moi 10 exercices de niveau 9ème sur les fractions. »

Cette fonctionnalité devra être contrôlée et validée pédagogiquement lorsque les résultats sont utilisés dans un contexte éducatif important.

## 10.4. Parcours personnalisé

Au lieu de présenter des milliers de contenus :

> **Voici ce que tu peux travailler maintenant.**

## 10.5. Assistant du mentor

L'IA peut aider les professionnels à :

- préparer des exercices ;
- structurer un cours ;
- créer des quiz ;
- préparer une séance ;
- générer des variantes d'exercices.

## 10.6. Positionnement

SCHOOL ON ne doit pas chercher à remplacer le professeur.

Le positionnement peut être :

> **IA + professeur + apprenant**

L'IA aide à personnaliser et accélérer l'apprentissage ; le mentor apporte l'accompagnement humain.

---

# 11. Simplicité d'utilisation

L'un des critères d'évaluation est :

> « Une personne non technique doit pouvoir comprendre l'application en environ 30 secondes. »

Cette contrainte doit influencer directement l'interface.

## 11.1. Quatre actions principales

La page d'accueil peut être organisée autour de :

### 📚 APPRENDRE
Trouver un cours.

### 📝 S'ENTRAÎNER
Faire des quiz et examens.

### 👨🏾‍🏫 TROUVER UN MENTOR
Trouver quelqu'un pour m'aider.

### 🤝 COMMUNAUTÉ
Poser une question et s'entraider.

Une cinquième entrée peut être :

### 🤖 SCHOOL ON AI
Demander de l'aide.

## 11.2. Principe

L'utilisateur ne devrait pas avoir besoin de comprendre :

- l'architecture technique ;
- les APIs ;
- les modèles IA ;
- les systèmes de paiement ;
- la blockchain ;
- les bases de données.

Il doit simplement comprendre :

> **« Qu'est-ce que je peux faire ici ? »**

---

# 12. Robustesse technique

La robustesse ne signifie pas d'utiliser le plus grand nombre de technologies.

Le principe doit être :

> **Utiliser les standards et infrastructures existants plutôt que réinventer la roue.**

## 12.1. Paiements

Utiliser des prestataires et APIs de paiement adaptés plutôt que créer son propre système bancaire.

## 12.2. Authentification

Utiliser des mécanismes et protocoles standards.

## 12.3. Géolocalisation

Utiliser des services de localisation existants tout en limitant l'exposition des données.

## 12.4. IA

Utiliser des modèles et APIs existants plutôt que développer un modèle fondamental depuis zéro.

## 12.5. Données

Séparer clairement :

- utilisateurs ;
- mentors ;
- cours ;
- réservations ;
- paiements ;
- progression ;
- quiz ;
- communauté.

## 12.6. Paiements et webhooks

Le système de paiement doit être conçu autour des événements confirmés par le prestataire.

Exemple :

```text
Création paiement
      ↓
Prestataire
      ↓
Webhook
      ↓
SCHOOL ON
      ↓
Mise à jour du statut
```

Il ne faut pas considérer qu'un simple clic côté navigateur constitue une preuve de paiement.

---

# 13. Architecture fonctionnelle simplifiée

La structure actuelle du projet comprend notamment :

- Utilisateurs ;
- Courses ;
- Progression ;
- Bookings ;
- Payments ;
- Forum.

La documentation actuelle prévoit déjà des modèles pour `CustomUser`, `TutorProfile`, `Course`, `Lesson`, `Quiz`, `Enrollment`, `LessonProgress`, `QuizAttempt`, `Booking`, `Payment`, `ForumThread` et `ForumPost`.

La nouvelle vision doit maintenant faire évoluer ces modèles selon les fonctionnalités réellement retenues.

---

# 14. MVP recommandé

Il faut éviter de développer toutes les idées en même temps.

## SCHOOL ON V1 — Gitega

### Apprenant

- compte ;
- cours ;
- leçons ;
- quiz ;
- progression ;
- préparation 9ème/examens.

### Mentor

- profil professionnel ;
- demande de vérification ;
- disponibilité ;
- recherche ;
- réservation.

### Communauté

- questions ;
- réponses ;
- signalement.

### IA

- assistant pédagogique ;
- aide à la compréhension ;
- recommandations simples.

### Paiement

- un ou deux moyens de paiement locaux au départ ;
- statuts de transaction ;
- paiement sécurisé ;
- confirmation ;
- litiges.

### Sécurité

- vérification ;
- réputation ;
- signalement ;
- blocage ;
- règles de rencontre.

---

# 15. Les trois critères de compétition

## A. Pertinence humaine et sociale

Question du jury :

> **Quel problème réel résolvez-vous ?**

Réponse conceptuelle :

> SCHOOL ON cherche à réduire la difficulté qu'un apprenant peut rencontrer lorsqu'il doit trouver la bonne ressource, comprendre une notion, s'entraîner, mesurer sa progression et accéder à un accompagnement humain de confiance.

Le projet doit partir de situations réelles observables à Gitega.

---

## B. Simplicité d'usage

Question :

> **Quelqu'un qui n'est pas technique peut-il comprendre l'application immédiatement ?**

Objectif :

> ouvrir SCHOOL ON → comprendre les quatre actions principales → commencer.

La technologie doit être invisible derrière une expérience simple.

---

## C. Robustesse technique

Question :

> **Le projet est-il construit proprement ?**

Réponse :

- architecture claire ;
- protocoles standards ;
- APIs existantes ;
- webhooks pour les paiements ;
- gestion explicite des statuts ;
- sécurité des données ;
- séparation des responsabilités ;
- validation côté serveur ;
- gestion des erreurs ;
- logs et traçabilité ;
- aucune dépendance inutile à une technologie « à la mode ».

---

# 16. Ce que SCHOOL ON ne doit PAS devenir

Pour rester concentré, il faut également définir les limites.

SCHOOL ON ne doit pas essayer immédiatement de devenir :

- YouTube ;
- ChatGPT ;
- une banque ;
- un réseau social généraliste ;
- une application de rencontres ;
- une application de géolocalisation ;
- une marketplace générale.

La plateforme doit rester centrée sur :

> **L'apprentissage et l'accompagnement de l'apprenant.**

---

# 17. Vision à long terme

Si le modèle fonctionne à Gitega, SCHOOL ON peut progressivement évoluer.

### Phase 1 — Gitega

Validation du problème et du comportement des utilisateurs.

### Phase 2 — Burundi

Extension à d'autres villes et établissements.

### Phase 3 — Afrique de l'Est

Adaptation à plusieurs contextes éducatifs et linguistiques.

### Phase 4 — Écosystème éducatif

Développement progressif :

- application mobile ;
- IA plus avancée ;
- mode hors ligne ;
- certifications ;
- écoles partenaires ;
- institutions ;
- nouveaux moyens de paiement ;
- messagerie ;
- recommandations personnalisées.

---

# 18. La phrase centrale du projet

La présentation de SCHOOL ON devrait pouvoir être résumée ainsi :

> **SCHOOL ON ne cherche pas simplement à donner accès à davantage de contenu. Elle cherche à accompagner l'apprenant : apprendre, pratiquer, comprendre ses difficultés, obtenir de l'aide et progresser.**

Et la boucle fondamentale est :

> **APPRENDRE → S'ENTRAÎNER → IDENTIFIER SES DIFFICULTÉS → OBTENIR DE L'AIDE → PROGRESSER**

---

# 19. Questions auxquelles l'équipe doit encore répondre

Avant de considérer cette vision comme définitive, l'équipe doit décider :

1. Quels établissements ou catégories d'apprenants de Gitega seront ciblés en premier ?
2. Quel est le premier problème observable que SCHOOL ON veut résoudre ?
3. Quels moyens de paiement seront réellement disponibles dans la première version ?
4. Quel prestataire permettra le paiement et les éventuels mécanismes de retenue/libération des fonds ?
5. Quelles informations seront nécessaires pour vérifier un mentor ?
6. Qui valide les mentors ?
7. Quelle commission SCHOOL ON prendra-t-elle ?
8. Quelles fonctionnalités seront gratuites ?
9. Quelle fonctionnalité IA sera disponible dans le MVP ?
10. Quelles données scolaires peuvent légalement et techniquement être utilisées ?
11. Comment gérer les litiges entre étudiant et mentor ?
12. Quelles règles précises encadreront les rencontres physiques ?
13. Quelles fonctionnalités seront volontairement repoussées après le MVP ?

Ces décisions permettront de passer d'une **vision de plateforme** à un **produit réellement exploitable**.

---

# 20. Conclusion

SCHOOL ON possède plusieurs briques :

**Cours — Quiz — Examens — IA — Mentors — Communauté — Progression — Tuteurs — Paiements.**

Mais ces briques ne doivent pas être présentées comme une simple liste de fonctionnalités.

Elles doivent fonctionner ensemble autour d'une seule idée :

> **Aider une personne à passer de « je veux apprendre » à « je progresse réellement ».**

C'est cette cohérence qui doit guider le design, le développement, la sécurité, le modèle économique et la présentation du projet.
