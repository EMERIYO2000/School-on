# SCHOOL ON --- User Flows

## 1. Première entrée

``` text
Splash
  ↓
Welcome / présentation
  ↓
Connexion OU Inscription
  ↓
Création du compte
  ↓
Choix du parcours
  ├── Apprenant
  ├── Mentor
  └── Décider plus tard
```

### Règle

Le rôle n'est pas sélectionné sur l'écran de connexion.

La connexion sert à authentifier l'utilisateur. Le parcours est choisi
après la création du compte.

------------------------------------------------------------------------

## 2. Parcours apprenant

``` text
Inscription
  ↓
Choix "Apprenant"
  ↓
Dashboard
  ↓
Explorer les cours
  ↓
Détail du cours
  ↓
Inscription / accès
  ↓
Apprentissage
  ↓
Chapitres
  ↓
Quiz / exercices
  ↓
Progression
  ↓
Fin du cours
  ↓
Éligibilité à la certification
  ↓
Certificat
```

### Écrans clés

-   Dashboard
-   Catalogue de cours
-   Détail d'un cours
-   Lecteur de cours
-   Vue chapitre
-   Quiz
-   Résultats du quiz
-   Progression
-   Certification
-   Certificat

------------------------------------------------------------------------

## 3. Parcours mentor

``` text
Création du compte
  ↓
Choix "Mentor"
  ↓
Profil / candidature mentor
  ↓
Informations de vérification
  ↓
Soumission
  ↓
Vérification administrative
  ├── En attente
  ├── Approuvé
  └── Rejeté / à corriger
  ↓
Mentor vérifié
  ↓
Dashboard Mentor
  ↓
Créer / gérer des cours
  ↓
Gérer les apprenants
  ↓
Gérer les réservations
```

La vérification doit être présentée comme un processus de confiance et
non comme une promesse absolue de compétence.

------------------------------------------------------------------------

## 4. Parcours "Décider plus tard"

``` text
Création du compte
  ↓
Décider plus tard
  ↓
Expérience générale
  ↓
Choisir son parcours ultérieurement
```

L'interface doit permettre de continuer sans forcer immédiatement un
choix définitif.

------------------------------------------------------------------------

## 5. Réservation d'un mentor

``` text
Mentors
  ↓
Liste des mentors
  ↓
Profil public du mentor
  ↓
Choisir une session
  ↓
Date / heure / mode
  ↓
Résumé de la réservation
  ↓
Confirmation
  ↓
Réservation en attente / confirmée
  ↓
Session
  ↓
Session terminée
  ↓
Mise à jour de l'état de la réservation
```

### UX

Afficher clairement :

-   identité publique du mentor
-   domaines d'expertise
-   statut de vérification
-   disponibilité
-   type de session
-   durée
-   prix lorsqu'il existe
-   état de la réservation

Les informations privées de vérification ne doivent jamais être exposées
dans le profil public.

------------------------------------------------------------------------

## 6. Parcours certification

``` text
Cours
  ↓
Progression
  ↓
Quiz / évaluations
  ↓
Conditions de fin
  ↓
Cours terminé
  ↓
Validation de certification
  ↓
Génération du certificat
  ↓
Signature du mentor si applicable
  ↓
Certificat disponible
  ↓
Consulter / télécharger / vérifier
```

L'interface doit distinguer :

-   cours en cours
-   cours terminé
-   certification en attente
-   certificat disponible

------------------------------------------------------------------------

## 7. États importants

Chaque flow doit prévoir :

-   Loading
-   Empty
-   Error
-   Success
-   Disabled
-   Pending
-   Unauthorized
-   Forbidden
-   Session expired

## 8. Navigation flow principle

Ne jamais créer un écran sans prévoir :

``` text
Entrée
  ↓
Action principale
  ↓
Résultat
  ↓
Prochaine étape
```

Les utilisateurs doivent pouvoir comprendre où continuer même lorsqu'une
opération échoue.
