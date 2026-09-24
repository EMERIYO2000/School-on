# SCHOOL ON — Parcours Utilisateur & Mentor

> **Document de conception — UX, Frontend & Backend**
>
> Version : 1.0  
> Statut : Proposition de conception  
> Périmètre : inscription, profil apprenant, candidature mentor, vérification, validation administrative et entrée dans l'application.

---

## 1. Objectif du document

Ce document décrit le parcours complet d'un utilisateur dans School On, depuis l'ouverture de l'application jusqu'à son entrée dans le dashboard.

Il décrit également le parcours spécifique d'un utilisateur qui souhaite devenir **Mentor**.

L'objectif est de fournir une base commune permettant au :

- Frontend de comprendre les écrans et les états à afficher ;
- Backend de comprendre les données, statuts et transitions à gérer ;
- équipe produit de comprendre les règles de sécurité et de confiance ;
- équipe Admin de comprendre le processus de validation des mentors.

### Principe central

> **Créer un compte doit être simple. Devenir Mentor doit être un processus vérifié.**

Un utilisateur ne doit donc pas être obligé de subir toute la procédure de vérification mentor simplement pour utiliser School On comme apprenant.

---

# 2. Philosophie générale du parcours

School On distingue deux niveaux :

### Compte utilisateur

Tout utilisateur peut créer un compte et commencer à utiliser les fonctionnalités accessibles aux apprenants.

### Statut Mentor

Un utilisateur qui souhaite enseigner, proposer des cours ou effectuer des sessions de mentorat doit passer par un processus de vérification.

Architecture générale :

```text
                         SCHOOL ON
                             |
                       Création de compte
                             |
                     +-------+-------+
                     |               |
                 APPRENANT        MENTOR
                     |               |
              Profil simple      Candidature
                     |               |
                     |          Vérification
                     |               |
                     |        Validation Admin
                     |               |
                     |          Mentor vérifié
                     |               |
                     +-------+-------+
                             |
                         Dashboard
```

---

# 3. Parcours global

```text
Splash Screen
      |
      v
Page d'accueil / Welcome
      |
      +----> En savoir plus
      |
      +----> Politique de confidentialité
      |
      v
Connexion / Inscription
      |
      v
Compte créé
      |
      v
Choix du parcours
      |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
  Apprenant            Mentor          Décider plus tard
      |                   |
      |                   v
      |             Profil Mentor
      |                   |
      |             Vérification
      |                   |
      |             Review Admin
      |                   |
      |          +--------+--------+
      |          |                 |
      |          v                 v
      |       Approuvé           Refusé
      |          |
      |          v
      +------> Dashboard
```

---

# 4. Étape 0 — Splash Screen

## Objectif

Le Splash Screen est l'écran très court affiché au lancement de l'application.

Il doit rester minimal.

### Contenu

```text
          [LOGO SCHOOL ON]


             SCHOOL ON

       [Nom du groupe/startup]
```

### Éléments

- Logo School On
- Nom School On
- éventuellement nom du groupe ou de la startup

### Durée

Environ 1 à 2 secondes selon le chargement de l'application.

### Frontend

Le frontend gère l'affichage et le passage vers l'écran suivant.

### Backend

Aucune opération particulière n'est nécessaire.

---

# 5. Étape 1 — Welcome / Introduction

Après le Splash Screen, l'utilisateur arrive sur une page présentant brièvement School On.

Exemple :

```text
              [GRAND LOGO]

                SCHOOL ON

   Une plateforme intelligente pour
   apprendre, enseigner et s'entraider.

   Apprenez.
   Trouvez un mentor.
   Partagez vos connaissances.
   Progressez ensemble.

              [Continuer]

             En savoir plus

      Politique de confidentialité
```

## Objectif

Cette page doit répondre rapidement à la question :

> **Pourquoi School On existe-t-il ?**

Elle ne doit pas devenir une longue présentation marketing.

---

# 6. Page "En savoir plus"

L'utilisateur peut consulter une présentation plus détaillée.

## Qu'est-ce que School On ?

School On est une plateforme permettant aux apprenants d'accéder à des ressources éducatives, des cours, des quiz et des mentors, tout en permettant aux professionnels et enseignants de partager leurs connaissances et d'accompagner les apprenants.

## Ce que l'utilisateur peut faire

- Apprendre ;
- consulter des ressources ;
- suivre des cours ;
- trouver un mentor ;
- réserver une session ;
- effectuer des quiz ;
- participer à la communauté ;
- partager des connaissances ;
- proposer des cours ou du mentorat lorsqu'il est éligible.

Cette page peut être développée progressivement.

---

# 7. Politiques et informations légales

La première expérience doit permettre à l'utilisateur d'accéder facilement aux informations importantes.

Liens possibles :

- Politique de confidentialité ;
- Conditions d'utilisation ;
- Politique de sécurité et de confiance ;
- éventuellement politique de paiement/remboursement.

Ces informations doivent être accessibles avant ou pendant l'inscription.

---

# 8. Étape 2 — Connexion / Inscription

L'utilisateur arrive ensuite sur l'écran d'authentification.

Exemple :

```text
              Bienvenue sur School On

           [ Continuer avec Google ]

                     ou

              [ Adresse e-mail ]

                 [ Mot de passe ]

                    [ S'inscrire ]

           Vous avez déjà un compte ?
                    Connexion
```

Selon les choix techniques de School On, l'authentification peut également supporter :

- numéro de téléphone ;
- OTP ;
- Google ;
- email + mot de passe.

## Principe UX

L'inscription doit rester courte.

Il ne faut pas demander immédiatement :

- certificat ;
- adresse complète ;
- compétences détaillées ;
- documents ;
- localisation GPS ;
- expérience professionnelle ;
- etc.

Ces informations appartiennent au parcours Mentor ou au profil complémentaire.

---

# 9. Étape 3 — Création du compte

Une fois l'authentification réussie :

```text
Utilisateur
     |
     v
Compte créé
     |
     v
Choix du parcours
```

Le compte utilisateur est donc créé avant de demander à l'utilisateur de devenir Mentor.

---

# 10. Étape 4 — Choix du parcours

Écran proposé :

```text
        Comment souhaitez-vous
           utiliser School On ?

+----------------------------------+
|                                  |
|           APPRENANT              |
|                                  |
|  Apprendre, pratiquer, trouver   |
|  des ressources et des mentors.  |
|                                  |
+----------------------------------+

+----------------------------------+
|                                  |
|             MENTOR               |
|                                  |
|  Partager vos connaissances et   |
|  accompagner des apprenants.     |
|                                  |
+----------------------------------+

        Je déciderai plus tard
```

## Pourquoi proposer "Je déciderai plus tard" ?

Parce qu'un utilisateur peut vouloir :

- explorer l'application ;
- apprendre ;
- consulter les cours ;
- comprendre School On ;

sans savoir immédiatement s'il souhaite devenir Mentor.

Cela évite de forcer un choix prématuré.

---

# 11. Parcours APPRENANT

Le parcours apprenant doit être rapide.

## Informations de base possibles

```text
Prénom
Nom
Nom d'utilisateur
Date de naissance
Ville
Photo de profil (optionnelle)
```

Certaines informations peuvent être obligatoires selon les règles finales du produit.

---

# 12. Intérêts de l'apprenant

School On peut demander :

```text
Quels sont vos domaines d'intérêt ?

[ ] Informatique
[ ] Mathématiques
[ ] Sciences
[ ] Design
[ ] Business
[ ] Langues
[ ] Programmation
[ ] etc.
```

Ces informations peuvent servir à :

- personnaliser le contenu ;
- recommander des cours ;
- recommander des mentors ;
- personnaliser le dashboard ;
- améliorer les recommandations futures.

## Important

Cette étape peut être **skippable**.

L'utilisateur doit pouvoir choisir :

```text
Passer pour l'instant
```

---

# 13. Profil progressif

School On ne doit pas obliger l'utilisateur à remplir tout son profil au premier lancement.

On peut utiliser un système de progression :

```text
Votre profil est complété à 60 %

████████████░░░░

Ajoutez vos matières préférées
Ajoutez une photo
Ajoutez votre niveau scolaire
```

L'utilisateur peut compléter son profil progressivement.

### Principe

> **Progressive profiling : demander les informations au moment où elles deviennent utiles.**

---

# 14. Entrée dans l'application

Après l'inscription :

```text
             🎉 Bienvenue sur School On

                       |
                       v

                  DASHBOARD
```

L'utilisateur peut alors accéder aux fonctionnalités autorisées.

---

# 15. Parcours MENTOR

Le parcours Mentor est différent.

Un utilisateur possédant un compte School On n'est pas automatiquement considéré comme Mentor.

Pour devenir Mentor :

```text
Utilisateur
    |
    v
"Devenir Mentor"
    |
    v
Candidature Mentor
    |
    v
Vérification
    |
    v
Validation Admin
    |
    v
Mentor vérifié
```

---

# 16. Étape Mentor — Informations personnelles

Le candidat fournit les informations nécessaires à son identité.

Exemple :

```text
Nom légal
Prénom
Date de naissance
Pays
Ville
Téléphone
Adresse
Photo de profil
```

## Protection de l'adresse

L'adresse exacte ne doit pas nécessairement être publique.

Le profil public peut afficher :

```text
Gitega, Burundi
```

plutôt que :

```text
Adresse exacte / numéro de maison
```

Les informations sensibles doivent rester protégées.

---

# 17. Localisation

School On ne doit pas demander une autorisation GPS permanente simplement pour créer un profil Mentor.

Il faut distinguer :

### Localisation du profil

Exemple :

```text
Pays : Burundi
Ville : Gitega
```

### Localisation précise

Elle peut être demandée uniquement lorsqu'une fonctionnalité particulière en a réellement besoin.

Par exemple :

```text
Réservation d'une rencontre
        |
        v
Besoin de localisation
        |
        v
Demande de permission
```

## Principe

> La localisation précise ne doit jamais être publiquement exposée sans raison.

---

# 18. Vérification d'identité

La vérification d'identité répond à une question :

> **La personne est-elle réellement celle qu'elle prétend être ?**

Documents possibles :

```text
Carte nationale
Passeport
Permis de conduire
```

Selon les possibilités techniques et réglementaires de School On.

Une vérification selfie/vidéo peut éventuellement être utilisée pour vérifier que la personne correspond au document.

### Important

La vérification d'identité et la vérification des compétences sont deux choses différentes.

---

# 19. Vérification des compétences

La deuxième question est :

> **Cette personne possède-t-elle réellement les compétences qu'elle revendique ?**

Le formulaire Mentor doit donc demander :

```text
Domaine principal

Niveau de compétence

Années d'expérience

Expérience professionnelle

Formation

Certifications

Portfolio / réalisations
```

Exemple :

```text
Domaine :
Programmation

Spécialité :
JavaScript / Web

Expérience :
3 ans

Niveau déclaré :
Avancé
```

---

# 20. Documents justificatifs

Le candidat peut fournir :

```text
Diplôme
Certificat
Attestation
Licence professionnelle
Preuve d'expérience
Portfolio
Autres documents pertinents
```

Mais :

> **Un document uploadé ne doit jamais être considéré comme une preuve absolue.**

Un certificat peut être falsifié ou appartenir à quelqu'un d'autre.

---

# 21. Modèle de confiance en plusieurs couches

School On doit construire la confiance progressivement.

```text
                 IDENTITÉ
                    +
               DOCUMENTS
                    +
              COMPÉTENCES
                    +
        EXPÉRIENCE / PORTFOLIO
                    +
               ÉVALUATION
                    +
          VALIDATION HUMAINE
                    +
       AVIS APRÈS VRAIES SESSIONS
                    +
        SYSTÈME DE SIGNALEMENT
                    |
                    v
          ÉCOSYSTÈME DE CONFIANCE
```

Aucune couche seule ne garantit que le Mentor est parfaitement qualifié.

---

# 22. Vérification des documents

Pour certaines qualifications, l'équipe Admin peut vérifier les informations auprès de la source lorsque cela est possible.

Exemple :

```text
Diplôme
   |
   v
Université / établissement
   |
   v
Vérification des informations
```

Pour une licence ou une qualification professionnelle :

```text
Qualification
   |
   v
Organisation / organisme concerné
   |
   v
Vérification
```

Si la vérification externe n'est pas possible, School On peut utiliser d'autres éléments :

- portfolio ;
- expérience ;
- références ;
- test ;
- entretien.

---

# 23. Les mentors sans diplôme

L'absence de diplôme ne signifie pas automatiquement qu'une personne n'a aucune compétence.

Un Mentor peut posséder une expérience réelle sans disposer d'un diplôme correspondant.

Dans ce cas :

```text
Expérience
+
Portfolio
+
Références
+
Test de compétence
+
Entretien éventuel
```

peuvent participer à la décision.

La procédure exacte peut dépendre du domaine.

---

# 24. Test de compétence

School On peut ajouter un système d'évaluation des compétences.

Exemple :

### Mentor JavaScript

```text
Test JavaScript

20 questions
+
1 problème pratique
```

### Mentor Mathématiques

```text
Test Mathématiques
+
résolution d'un problème
+
explication du raisonnement
```

### Mentor Design

```text
Portfolio
+
exercice pratique
```

L'objectif n'est pas nécessairement de créer un examen universitaire complet.

Il s'agit d'ajouter une preuve supplémentaire aux autres éléments.

---

# 25. Entretien Mentor

Pour certaines catégories, School On peut demander un entretien avec un administrateur.

Exemple :

```text
Entretien vidéo

- Présentez-vous.
- Quel est votre domaine ?
- Quelle est votre expérience ?
- Pourquoi voulez-vous devenir Mentor ?
- Comment accompagneriez-vous un apprenant ?
```

L'entretien n'est pas nécessairement obligatoire pour tous les domaines.

Il peut être utilisé lorsque le niveau de risque ou le besoin de vérification est plus élevé.

---

# 26. Statuts de vérification

Le backend doit gérer plusieurs statuts.

```text
DRAFT
PENDING_VERIFICATION
UNDER_REVIEW
NEEDS_INFORMATION
VERIFIED
REJECTED
SUSPENDED
```

## Signification

### DRAFT

Candidature commencée mais pas terminée.

### PENDING_VERIFICATION

La candidature est envoyée et attend une vérification.

### UNDER_REVIEW

Un administrateur examine la candidature.

### NEEDS_INFORMATION

Des informations ou documents supplémentaires sont nécessaires.

### VERIFIED

Le Mentor a été approuvé.

### REJECTED

La candidature a été refusée.

### SUSPENDED

Le statut Mentor est temporairement suspendu après validation.

---

# 27. Badges / niveaux de confiance

Le profil peut afficher différents états.

## Compte créé

```text
Compte créé
```

Aucune affirmation particulière sur les qualifications.

## Identité vérifiée

```text
✓ Identité vérifiée
```

School On a vérifié l'identité selon son processus.

## Mentor vérifié

```text
✓ Mentor vérifié
```

Le processus de validation School On a été complété.

## Expérience et réputation

Plus tard, le profil pourra afficher :

```text
4.8 ⭐
37 sessions
31 apprenants
98 % de présence
```

Ces informations doivent être basées sur des activités réelles.

---

# 28. Système d'avis

Les avis doivent être liés à de vraies interactions.

Règle recommandée :

> **Seul un apprenant ayant réellement effectué une session avec un Mentor peut laisser un avis.**

Cela réduit les faux avis.

Exemple :

```text
Mentor : Jean

✓ Identité vérifiée
✓ Mentor vérifié

4.8 ⭐

37 sessions
31 apprenants
98 % présence
```

---

# 29. Protection contre les faux avis

Le système ne doit pas permettre facilement :

```text
Faux compte
   |
   v
Fausse réservation
   |
   v
Faux avis 5 étoiles
```

Les avis doivent donc être liés à :

```text
Reservation
      |
      v
Session réalisée
      |
      v
Review
```

Le backend doit pouvoir vérifier cette relation.

---

# 30. Validation Admin

L'Admin doit avoir un tableau de contrôle.

Exemple :

```text
----------------------------------------
       MENTOR APPLICATION #1024
----------------------------------------

Identity
✓ Government ID

Profile
✓ Complete

Skills
✓ Mathematics
✓ Physics

Documents
✓ Diploma
✓ Teaching certificate

Assessment
Score : 86%

Interview
✓ Completed

----------------------------------------

[ APPROVE ]

[ REQUEST INFORMATION ]

[ REJECT ]
----------------------------------------
```

---

# 31. Historique des décisions

Le backend ne doit pas uniquement enregistrer :

```text
mentor.is_verified = True
```

Il faut garder un historique.

Exemple conceptuel :

```text
VerificationRecord

id
mentor_id
verification_type
status
reviewed_by
reviewed_at
reason
notes
document_reference
```

Cela permet de répondre plus tard à des questions comme :

> Pourquoi ce Mentor a-t-il été validé ?

ou :

> Qui a validé cette candidature ?

---

# 32. Signalement d'un Mentor

Chaque profil Mentor doit pouvoir être signalé.

Exemple :

```text
[ Signaler ce Mentor ]
```

Raisons possibles :

```text
Fausse identité
Fausse qualification
Comportement inapproprié
Fraude
Harcèlement
Problème pendant une session
Autre
```

---

# 33. Processus après signalement

```text
Signalement
     |
     v
Admin Review
     |
     v
Investigation
     |
     +---------------------+
     |                     |
     v                     v
Aucun problème       Problème confirmé
     |                     |
     v                     v
Clôture             Suspension
                           |
                           v
                    Décision Admin
```

Un Mentor peut donc être vérifié aujourd'hui et être suspendu plus tard si des éléments sérieux apparaissent.

---

# 34. Limite importante du système de vérification

School On ne doit pas communiquer une promesse impossible comme :

> "Tous nos mentors sont parfaitement qualifiés."

Une formulation plus correcte est :

> **"School On vérifie l'identité et les informations professionnelles des Mentors selon notre processus de vérification afin de renforcer la confiance et la sécurité de la communauté."**

La vérification réduit le risque mais ne constitue pas une garantie absolue.

---

# 35. Commission et paiements

La commission School On doit être expliquée clairement.

Elle peut concerner :

- cours payants ;
- sessions de mentorat ;
- réservations ;
- autres services payants.

Exemple :

```text
Cours : 10 000 FBU

Prix du cours          10 000 FBU
Commission School On    - X FBU
Revenu du Mentor         X FBU
```

La commission applicable doit être visible avant la transaction.

---

# 36. Où présenter la commission ?

Il est préférable d'avoir une page :

```text
Comment fonctionnent les paiements ?
```

avec :

- fonctionnement des paiements ;
- commission School On ;
- revenu du Mentor ;
- frais éventuels ;
- conditions de remboursement ;
- statut des transactions.

Il ne faut pas mélanger toutes ces informations avec le formulaire d'identité.

---

# 37. Architecture Backend proposée

Le compte utilisateur reste séparé des informations spécifiques au rôle.

```text
User
 |
 +---- Profile
 |
 +---- LearnerProfile
 |
 +---- MentorProfile
          |
          +---- MentorApplication
          |
          +---- MentorSkill
          |
          +---- Qualification
          |
          +---- VerificationRecord
          |
          +---- Assessment
          |
          +---- Interview
          |
          +---- Review
          |
          +---- MentorStatus
```

Cette séparation rend l'architecture plus évolutive.

---

# 38. Modèles conceptuels

## User

```text
User
- id
- email
- phone
- password
- authentication_provider
- is_active
- created_at
```

## Profile

```text
Profile
- user_id
- first_name
- last_name
- username
- date_of_birth
- country
- city
- profile_picture
- bio
```

## LearnerProfile

```text
LearnerProfile
- user_id
- education_level
- interests
- profile_completion
```

## MentorProfile

```text
MentorProfile
- user_id
- professional_bio
- city
- public_location
- mentor_status
- verified_at
```

---

# 39. MentorApplication

```text
MentorApplication
- id
- mentor_id
- status
- submitted_at
- reviewed_at
- reviewed_by
- rejection_reason
```

---

# 40. MentorSkill

```text
MentorSkill
- id
- mentor_id
- domain
- specialization
- declared_level
- years_of_experience
```

---

# 41. Qualification

```text
Qualification
- id
- mentor_id
- type
- institution
- title
- year
- document
- verification_status
```

---

# 42. VerificationRecord

```text
VerificationRecord
- id
- mentor_id
- verification_type
- status
- reviewed_by
- reviewed_at
- reason
- notes
- document_reference
```

Exemples de `verification_type` :

```text
IDENTITY
DOCUMENT
SKILL
EXPERIENCE
INTERVIEW
```

---

# 43. Assessment

```text
Assessment
- id
- mentor_id
- skill
- score
- status
- completed_at
```

---

# 44. MentorStatus

```text
DRAFT
PENDING_VERIFICATION
UNDER_REVIEW
NEEDS_INFORMATION
VERIFIED
REJECTED
SUSPENDED
```

---

# 45. Flux technique général

```text
Frontend
   |
   | Register / Login
   v
Authentication API
   |
   v
User
   |
   v
Profile
   |
   +--------------------+
   |                    |
   v                    v
LearnerProfile      MentorProfile
                         |
                         v
                  MentorApplication
                         |
                         v
                  Verification APIs
                         |
                         v
                    Admin Panel
                         |
                +--------+--------+
                |                 |
                v                 v
             APPROVE           REJECT
                |
                v
         MentorStatus =
             VERIFIED
```

---

# 46. Sécurité et confidentialité

Les informations suivantes doivent être considérées comme sensibles :

- documents d'identité ;
- certificats ;
- documents professionnels ;
- adresse exacte ;
- données de vérification ;
- éventuels selfies/vidéos de vérification.

Le système doit prévoir :

- accès restreint aux administrateurs autorisés ;
- stockage sécurisé ;
- contrôle des permissions ;
- journalisation des accès importants ;
- suppression ou conservation selon les règles de confidentialité ;
- chiffrement lorsque nécessaire ;
- séparation entre informations publiques et privées.

Les documents de vérification ne doivent pas être accessibles publiquement depuis le profil Mentor.

---

# 47. Informations publiques vs privées

## Profil public

```text
Nom affiché
Photo
Bio
Ville
Domaines
Compétences
Expérience
Badges de vérification
Avis
Statistiques pertinentes
```

## Informations privées

```text
Document d'identité
Adresse exacte
Numéro de document
Documents de vérification
Informations internes de validation
Notes Admin
Données sensibles de vérification
```

---

# 48. Parcours final recommandé

```text
                         SCHOOL ON
                             |
                             v
                      SPLASH SCREEN
                             |
                             v
                       WELCOME PAGE
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
        En savoir plus   Confidentialité   Continuer
                                             |
                                             v
                                  CONNEXION / INSCRIPTION
                                             |
                                             v
                                        COMPTE CRÉÉ
                                             |
                                             v
                                   CHOIX DU PARCOURS
                                             |
                  +--------------------------+--------------------------+
                  |                          |                          |
                  v                          v                          v
              APPRENANT                  MENTOR                 PLUS TARD
                  |                          |
                  v                          v
          Profil de base              Profil Mentor
                  |                          |
                  v                          v
          Intérêts optionnels          Identité
                  |                          |
                  v                          v
              DASHBOARD                Compétences
                                             |
                                             v
                                         Documents
                                             |
                                             v
                                      Test / Portfolio
                                             |
                                             v
                                      Entretien si besoin
                                             |
                                             v
                                      Review Admin
                                             |
                                  +----------+----------+
                                  |                     |
                                  v                     v
                              APPROUVÉ                REFUSÉ
                                  |
                                  v
                           MENTOR VÉRIFIÉ
                                  |
                                  v
                              DASHBOARD
```

---

# 49. Principes à retenir pour l'équipe

### Principe 1 — Inscription simple

Un utilisateur ne doit pas remplir un long formulaire simplement pour découvrir School On.

### Principe 2 — Mentor ≠ utilisateur normal

Le statut Mentor doit être obtenu après vérification.

### Principe 3 — Une seule preuve ne suffit pas

Un certificat uploadé ne doit pas être considéré comme une preuve absolue.

### Principe 4 — Identité ≠ compétence

Vérifier qu'une personne est bien elle-même ne prouve pas qu'elle maîtrise son domaine.

### Principe 5 — Vérification progressive

```text
Identité
+
Documents
+
Compétences
+
Expérience
+
Évaluation
+
Validation humaine
```

selon le niveau de risque et le domaine.

### Principe 6 — La confiance continue après validation

Les avis, signalements, statistiques de sessions et comportements doivent continuer à contribuer à la confiance.

### Principe 7 — Confidentialité

Les documents privés et l'adresse exacte ne doivent jamais devenir automatiquement publics.

### Principe 8 — Aucune garantie absolue

School On doit parler de **processus de vérification**, pas de garantie parfaite.

### Principe 9 — Traçabilité

Toutes les décisions importantes de vérification doivent pouvoir être retracées.

### Principe 10 — Évolutivité

Le système doit pouvoir accueillir plus tard :

- compte parent ;
- nouvelles catégories de Mentors ;
- nouvelles méthodes de vérification ;
- paiements ;
- réservation ;
- évaluations avancées ;
- systèmes de réputation ;
- autres partenaires de vérification.

---

# 50. Résumé produit

Le parcours School On doit être pensé comme deux niveaux :

```text
             NIVEAU 1
         CRÉER UN COMPTE
               |
               v
        UTILISER SCHOOL ON
               |
               v
           APPRENANT
```

et :

```text
             NIVEAU 2
       DEVENIR MENTOR
               |
               v
          CANDIDATURE
               |
               v
        VÉRIFICATION
               |
               v
        REVIEW ADMIN
               |
               v
       MENTOR VÉRIFIÉ
```

Le principe fondamental est donc :

> **School On doit rendre l'apprentissage facile d'accès, tout en rendant l'accès au statut de Mentor suffisamment vérifié pour construire un environnement de confiance.**
