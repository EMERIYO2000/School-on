# SCHOOL ON

## Système de Certification des Cours

**Version : 1.0**
**Statut : Spécification fonctionnelle et technique**
**Projet : School On**
**Module : Courses → Assessments → Certification**

---

# 1. Objectif

Le système de certification permet à School On de délivrer automatiquement un certificat à un apprenant lorsqu'il a satisfait les conditions de réussite d'un cours.

Le certificat doit être :

* généré automatiquement ;
* associé à un cours précis ;
* associé à un apprenant ;
* associé au mentor du cours lorsque le cours est dispensé par un mentor ;
* signé par le mentor ;
* signé par School On ;
* téléchargeable en PDF ;
* imprimable ;
* partageable ;
* vérifiable publiquement grâce à un identifiant unique et un QR Code.

L'objectif n'est pas simplement de produire un joli document PDF.

Le certificat doit constituer une **preuve vérifiable de réussite à un parcours d'apprentissage School On**.

---

# 2. Principe fondamental

School On ne doit pas délivrer automatiquement un certificat uniquement parce qu'un utilisateur a ouvert ou regardé un cours.

Le système doit distinguer :

```text
Inscription au cours
        ↓
Progression
        ↓
Contenu terminé
        ↓
Quiz / évaluations
        ↓
Projet ou évaluation finale
        ↓
Conditions de réussite
        ↓
Cours validé
        ↓
CERTIFICAT
```

Ainsi :

> Payer un cours ≠ obtenir automatiquement un certificat.

Et :

> Terminer un cours ≠ nécessairement réussir la certification.

Le certificat représente la **validation d'un parcours**, pas simplement l'accès à du contenu.

---

# 3. Intégration avec les fonctionnalités existantes

Le système de certification doit être intégré aux fonctionnalités déjà prévues dans School On.

Les principaux modules concernés sont :

```text
User
 │
 ├── Course
 │     │
 │     ├── Modules / Lessons
 │     │
 │     ├── Quiz
 │     │
 │     ├── Exercises
 │     │
 │     └── Final Assessment
 │
 ├── Mentor
 │
 └── Certificate
```

Le certificat dépend donc principalement de :

* l'utilisateur ;
* l'inscription au cours ;
* la progression ;
* les quiz ;
* les évaluations ;
* le mentor ;
* le cours.

---

# 4. Types de cours

Tous les cours School On ne doivent pas nécessairement produire le même type de certification.

## 4.1 Cours sans certification

Certains contenus peuvent être entièrement gratuits et destinés à la découverte.

Exemple :

* Introduction à Internet
* Découverte de l'IA
* Introduction au développement web

L'utilisateur peut obtenir :

```text
Attestation de participation
```

ou simplement :

```text
Cours terminé
```

---

## 4.2 Cours certifiants

Les cours plus structurés peuvent être certifiants.

Exemple :

```text
JavaScript Fundamentals
Python Fundamentals
UI/UX Design
Digital Marketing
Full-Stack Web Development
```

Ces cours disposent de conditions de réussite.

Exemple :

```text
Quiz minimum : 70 %
Progression : 100 %
Projet final : validé
```

---

# 5. Configuration de la certification dans un cours

Lorsqu'un mentor ou un administrateur crée un cours, il doit pouvoir définir si le cours est certifiant.

Exemple dans le formulaire de création :

```text
Certification

[✓] Ce cours délivre un certificat

Conditions de certification :

Progression minimale : 100 %

Score minimum des quiz : 70 %

Projet final requis : Oui

Validation du mentor : Oui
```

Pour certains cours :

```text
Projet final requis : Non
```

Pour d'autres :

```text
Projet final requis : Oui
```

---

# 6. Conditions de certification

Le backend doit permettre de définir plusieurs conditions.

## Condition 1 — Progression

L'apprenant doit avoir terminé le parcours requis.

Exemple :

```text
progress >= 100
```

ou, selon la logique du cours :

```text
all_required_lessons_completed = true
```

Il est préférable de considérer les éléments obligatoires plutôt qu'un simple pourcentage lorsque certains contenus sont optionnels.

---

# 7. Condition 2 — Quiz

Les quiz existants de School On doivent pouvoir participer à la certification.

Exemple :

```text
Score minimum : 70 %
```

Un cours peut contenir plusieurs quiz.

Exemple :

```text
Quiz 1 → 80 %
Quiz 2 → 75 %
Quiz 3 → 90 %
```

Le système peut être configuré selon le cours :

### Option A — moyenne minimale

```text
Moyenne des quiz >= 70 %
```

### Option B — chaque quiz obligatoire

```text
Quiz 1 >= 70 %
Quiz 2 >= 70 %
Quiz 3 >= 70 %
```

La configuration exacte doit être stockée dans le cours.

---

# 8. Condition 3 — Évaluation finale

Certains cours doivent avoir une évaluation finale.

Exemple :

```text
Final Assessment
Score minimum : 70 %
```

Le système doit pouvoir différencier :

```text
Quiz normal
```

et :

```text
Final Assessment
```

Le quiz final peut utiliser le système de quiz déjà prévu dans School On.

Il ne faut donc pas créer un deuxième système de questions inutilement.

---

# 9. Condition 4 — Projet final

Certains cours nécessitent un projet.

Exemple :

### Cours

```text
Full-Stack Web Development
```

### Projet final

> Construire une application web fonctionnelle.

Le mentor peut :

```text
Voir le projet
↓
Évaluer
↓
Attribuer un score
↓
Valider / Refuser
```

Exemple :

```text
Project score : 82 %
Status : APPROVED
```

---

# 10. Condition 5 — Validation du mentor

Pour les cours avec mentor, le mentor peut avoir une dernière validation.

Exemple :

```text
Toutes les conditions automatiques sont remplies.

        ↓

Certification en attente de validation du mentor.

        ↓

Mentor :
[ Valider la certification ]
```

Une fois validée :

```text
CERTIFICAT GÉNÉRÉ
```

Pour les cours entièrement automatisés :

```text
Mentor approval required = false
```

Le certificat peut alors être généré automatiquement.

---

# 11. Statut de progression vers la certification

L'apprenant doit pouvoir voir son état.

Exemple :

```text
Certification

Progression : 82 %

✓ Modules terminés
✓ Quiz minimum atteint
○ Projet final
○ Validation mentor

Certification :
EN COURS
```

Lorsque tout est terminé :

```text
✓ Modules terminés
✓ Quiz validés
✓ Projet final validé
✓ Validation mentor

CERTIFICATION DISPONIBLE
```

---

# 12. États du processus

Le backend peut utiliser les statuts suivants :

```text
NOT_STARTED
IN_PROGRESS
ELIGIBLE
PENDING_MENTOR_APPROVAL
CERTIFIED
```

Pour le certificat lui-même :

```text
VALID
REVOKED
```

---

# 13. Génération du certificat

Lorsque toutes les conditions sont satisfaites :

```text
CourseCompletion
       ↓
CertificationEligibility
       ↓
Certificate Creation
       ↓
PDF Generation
       ↓
QR Code Generation
       ↓
Certificate Available
```

Le certificat doit être généré **une seule fois** pour une réussite donnée.

Il faut éviter que l'utilisateur puisse générer :

```text
Certificate #001
Certificate #002
Certificate #003
```

pour le même cours sans raison.

---

# 14. Identifiant unique

Chaque certificat reçoit un identifiant unique.

Exemple :

```text
SO-CERT-2026-000184
```

ou :

```text
SO-2026-JS-000184
```

Cet identifiant doit être unique dans toute la base.

Il doit permettre de retrouver le certificat.

---

# 15. QR Code

Chaque certificat doit contenir un QR Code.

Le QR Code pointe vers une page publique de vérification.

Exemple :

```text
https://schoolon.app/verify/SO-CERT-2026-000184
```

Le QR Code ne doit pas contenir directement toutes les informations du certificat.

Il doit simplement permettre d'accéder à la vérification.

---

# 16. Page publique de vérification

La page :

```text
/verify/<certificate_id>
```

doit être accessible sans connexion.

Exemple :

```text
✓ CERTIFICAT AUTHENTIQUE

School On

Certificat de réussite

Nom :
DOD BUKUTO

Cours :
JavaScript Fundamentals

Mentor :
Jean Dupont

Date d'obtention :
22 septembre 2026

Certificate ID :
SO-CERT-2026-000184

Statut :
VALID
```

La page ne doit afficher que les informations que School On souhaite rendre publiques.

Il faut éviter d'exposer :

* numéro de téléphone ;
* email ;
* informations privées ;
* données de paiement ;
* informations personnelles inutiles.

---

# 17. Contenu du certificat PDF

Le certificat doit être au format :

```text
A4 Landscape
```

Structure recommandée :

```text
----------------------------------------------------

                     SCHOOL ON

       Une plateforme intelligente pour apprendre,
              enseigner et s'entraider


                    CERTIFICAT
                  DE RÉUSSITE


              Ce certificat est décerné à

                    [NOM APPRENANT]


        pour avoir complété avec succès le cours


             [NOM DU COURS]


             Niveau : [NIVEAU]
             Durée : [DURÉE]
             Date : [DATE]


      ___________________       ___________________
      Signature Mentor          Signature School On


      Certificate ID : SO-CERT-2026-000184

                         [QR CODE]

             Vérifier l'authenticité
                 de ce certificat

----------------------------------------------------
```

---

# 18. Informations dynamiques du certificat

Le PDF doit être généré à partir des données de la base.

Variables :

```text
{{student_name}}
{{course_title}}
{{mentor_name}}
{{course_level}}
{{course_duration}}
{{completion_date}}
{{certificate_id}}
{{verification_url}}
{{mentor_signature}}
{{school_on_signature}}
{{final_score}}
```

Certaines variables doivent être optionnelles.

Par exemple :

```text
{{final_score}}
```

ne doit pas être affiché si School On décide de ne pas afficher les scores sur les certificats.

---

# 19. Signature du mentor

Chaque mentor certifiant doit disposer d'une signature enregistrée.

Dans le profil mentor :

```text
Signature de certification

[ Upload signature ]

Formats :
PNG / JPG

Statut :
✓ Signature enregistrée
```

Le mentor ne doit pas pouvoir modifier la signature d'un certificat déjà délivré.

La signature utilisée au moment de la délivrance doit être conservée avec le certificat.

---

# 20. Signature School On

School On dispose également d'une signature officielle.

Elle peut être configurée dans l'administration.

Exemple :

```text
Admin Settings

Certification
    └── School On Signature
```

Cette signature sera utilisée lors de la génération du certificat.

---

# 21. Important : snapshot des données

Une fois le certificat généré, certaines informations doivent être figées.

Exemple :

Un mentor s'appelle :

```text
Jean Dupont
```

Il délivre un certificat.

Six mois plus tard, il change son nom de profil.

Le certificat historique ne doit pas changer.

Le certificat doit conserver :

```text
mentor_name_at_issue
mentor_signature_at_issue
course_title_at_issue
student_name_at_issue
```

Le PDF représente donc l'état du certificat au moment de sa délivrance.

---

# 22. Modèle Certificate

Proposition Django :

```python
class Certificate(models.Model):

    certificate_id = models.CharField(
        max_length=100,
        unique=True
    )

    student = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="certificates"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="certificates"
    )

    mentor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="issued_certificates",
        null=True,
        blank=True
    )

    student_name = models.CharField(max_length=255)

    course_title = models.CharField(max_length=255)

    mentor_name = models.CharField(
        max_length=255,
        blank=True
    )

    issue_date = models.DateTimeField()

    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    mentor_signature = models.ImageField(
        upload_to="certificates/signatures/",
        null=True,
        blank=True
    )

    school_on_signature = models.ImageField(
        upload_to="certificates/signatures/"
    )

    verification_token = models.CharField(
        max_length=255,
        unique=True
    )

    pdf_file = models.FileField(
        upload_to="certificates/pdfs/",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="VALID"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
```

---

# 23. Relation avec l'inscription au cours

Il doit exister une relation entre :

```text
Student
Course
Enrollment
Certificate
```

Exemple :

```text
User
  │
  └── Enrollment
          │
          ├── Course
          ├── progress
          ├── quiz_results
          ├── final_project
          └── certificate
```

Un certificat ne doit être délivré qu'à partir d'une inscription valide au cours.

---

# 24. Exemple de modèle Enrollment

Si votre système possède déjà un modèle d'inscription, il faut le réutiliser.

Il peut contenir :

```text
Enrollment
├── student
├── course
├── status
├── progress
├── started_at
├── completed_at
└── completed
```

Il n'est pas nécessaire de créer un deuxième système d'inscription uniquement pour la certification.

---

# 25. Relation avec les quiz

Le système de certification doit utiliser les résultats des quiz existants.

Exemple :

```text
Quiz
├── Course
├── Questions
└── Answers

QuizAttempt
├── User
├── Quiz
├── score
├── passed
└── completed_at
```

Le moteur de certification peut ensuite vérifier :

```python
if quiz_attempt.score >= course.minimum_quiz_score:
    ...
```

ou :

```python
if all_required_quizzes_passed:
    ...
```

La logique exacte dépend de la configuration du cours.

---

# 26. Ne pas dupliquer le système de quiz

Important pour le backend :

Il ne faut PAS créer :

```text
Course Quiz System
```

et :

```text
Certification Quiz System
```

Le système de certification doit simplement **consommer les résultats du système de quiz existant**.

Architecture :

```text
             QUIZ SYSTEM
                  │
                  │ résultats
                  ▼
        CERTIFICATION ENGINE
                  │
          vérifie les règles
                  │
                  ▼
             CERTIFICATE
```

---

# 27. Certification Engine

Il est recommandé d'avoir une logique/service séparé.

Exemple :

```text
services/
    certification_service.py
```

Responsabilités :

```text
check_eligibility()
calculate_final_score()
validate_requirements()
create_certificate()
generate_pdf()
generate_qr_code()
revoke_certificate()
```

Exemple conceptuel :

```python
def check_certificate_eligibility(enrollment):

    course = enrollment.course

    if not enrollment.completed:
        return False

    if course.requires_quiz:
        if not quizzes_passed(enrollment):
            return False

    if course.requires_final_project:
        if not project_approved(enrollment):
            return False

    if course.requires_mentor_approval:
        return "PENDING_MENTOR_APPROVAL"

    return True
```

---

# 28. API Backend

Le backend doit fournir des endpoints permettant au frontend de gérer le système.

Exemple :

```text
GET /api/courses/{course_id}/certification-status/
```

Retour :

```json
{
  "eligible": false,
  "progress": 82,
  "requirements": {
    "course_completion": true,
    "quiz": true,
    "final_project": false,
    "mentor_approval": false
  }
}
```

---

# 29. Liste des certificats

```text
GET /api/certificates/
```

Retour :

```json
{
  "results": [
    {
      "certificate_id": "SO-CERT-2026-000184",
      "course": "JavaScript Fundamentals",
      "issued_at": "2026-09-22",
      "status": "VALID"
    }
  ]
}
```

---

# 30. Détails d'un certificat

```text
GET /api/certificates/{certificate_id}/
```

Retour :

```json
{
  "certificate_id": "SO-CERT-2026-000184",
  "student_name": "DOD BUKUTO",
  "course_title": "JavaScript Fundamentals",
  "mentor_name": "Jean Dupont",
  "issue_date": "2026-09-22",
  "status": "VALID",
  "verification_url": "/verify/SO-CERT-2026-000184",
  "pdf_url": "..."
}
```

---

# 31. Téléchargement du PDF

```text
GET /api/certificates/{certificate_id}/download/
```

Le backend renvoie le fichier PDF.

Le frontend affiche simplement :

```text
[Télécharger le certificat]
```

---

# 32. Vérification publique

Endpoint :

```text
GET /api/public/certificates/verify/{certificate_id}/
```

Il doit être accessible sans authentification.

Retour :

```json
{
  "valid": true,
  "certificate_id": "SO-CERT-2026-000184",
  "student_name": "DOD BUKUTO",
  "course_title": "JavaScript Fundamentals",
  "mentor_name": "Jean Dupont",
  "issue_date": "2026-09-22"
}
```

---

# 33. Frontend — Page du cours

La page du cours doit indiquer clairement si celui-ci est certifiant.

Exemple :

```text
JavaScript Fundamentals

✓ Cours certifiant

À la fin de ce cours :

✓ 8 modules
✓ 5 quiz
✓ 1 projet final
✓ Évaluation
✓ Certificat School On
```

---

# 34. Frontend — Progression

Dans le dashboard du cours :

```text
Votre progression

████████████████░░ 82 %

Certification

✓ Modules obligatoires
✓ Quiz
○ Projet final
○ Validation mentor

Il vous reste 2 étapes pour obtenir
votre certificat.
```

---

# 35. Frontend — Quand le certificat est disponible

Afficher une notification claire :

```text
🎓 Félicitations !

Vous avez réussi le cours
"JavaScript Fundamentals".

Votre certificat School On est maintenant disponible.

[Voir mon certificat]
[ Télécharger PDF ]
```

---

# 36. Dashboard — Mes certificats

Créer une section :

```text
Dashboard
│
├── Mes cours
├── Mes quiz
├── Mes mentors
├── Mes réservations
├── Communauté
└── Mes certificats
```

Page :

```text
MES CERTIFICATS

┌──────────────────────────────────┐
│ JavaScript Fundamentals          │
│ Certifié le 22 septembre 2026    │
│                                  │
│ [Voir] [Télécharger] [Partager]  │
└──────────────────────────────────┘
```

---

# 37. Page Certificate Preview

Avant téléchargement :

```text
┌────────────────────────────────────┐
│                                    │
│        APERÇU DU CERTIFICAT        │
│                                    │
│         [CERTIFICAT A4]            │
│                                    │
└────────────────────────────────────┘

[ Télécharger PDF ]

[ Imprimer ]

[ Vérifier ]

[ Copier le lien ]
```

---

# 38. Impression

Le certificat doit être optimisé pour l'impression.

Format recommandé :

```text
A4
Landscape
300 DPI pour les éléments raster
```

Le PDF doit éviter :

* éléments coupés ;
* texte trop petit ;
* couleurs illisibles en impression ;
* QR Code trop petit ;
* signature floue.

---

# 39. Partage

L'utilisateur peut partager le lien de vérification.

Exemple :

```text
https://schoolon.app/verify/SO-CERT-2026-000184
```

Bouton :

```text
[ Copier le lien ]
```

Plus tard, vous pouvez ajouter :

```text
Partager sur WhatsApp
Partager sur LinkedIn
Partager par email
```

Mais ces intégrations ne sont pas obligatoires pour le MVP.

---

# 40. Révocation d'un certificat

Un administrateur doit pouvoir révoquer un certificat.

Exemple :

```text
Certificate
SO-CERT-2026-000184

Status:
VALID

[ Révoquer le certificat ]
```

Après révocation :

```text
Status:
REVOKED
```

La page publique affiche :

```text
⚠ CERTIFICAT RÉVOQUÉ

Ce certificat n'est plus considéré comme valide.
```

Le PDF historique ne doit pas être supprimé immédiatement.

La vérification en ligne doit simplement indiquer son nouveau statut.

---

# 41. Pourquoi conserver le certificat révoqué ?

Pour éviter qu'une personne continue à présenter un ancien certificat comme valide.

Exemple :

```text
Ancien PDF
    ↓
QR Code
    ↓
School On
    ↓
REVOKED
```

Le document existe toujours mais son statut officiel est mis à jour.

---

# 42. Sécurité

Le système doit empêcher un utilisateur de fabriquer facilement un faux certificat.

Mesures minimales :

### Certificate ID unique

```text
unique=True
```

### Token de vérification

Utiliser un token aléatoire suffisamment difficile à deviner.

### Vérification serveur

Le frontend ne doit jamais décider :

```text
certificate.valid = true
```

La validation doit venir du backend.

### PDF généré côté serveur

Le certificat officiel doit être généré par le backend.

### Page publique

La vérification doit interroger la base de données.

---

# 43. Ce que le frontend ne doit PAS faire

Le frontend ne doit pas :

* générer lui-même le numéro officiel ;
* décider qu'un utilisateur est certifié ;
* modifier le statut `VALID` ;
* fabriquer la signature School On ;
* considérer un quiz comme réussi sans validation backend ;
* générer un certificat officiel uniquement à partir des données locales.

Le frontend affiche.

Le backend décide.

---

# 44. Ce que le backend doit contrôler

Le backend est responsable de :

```text
✓ Vérification des conditions
✓ Calcul de l'éligibilité
✓ Validation du score
✓ Validation du projet
✓ Validation mentor
✓ Création du Certificate ID
✓ Génération QR
✓ Génération PDF
✓ Stockage du certificat
✓ Statut du certificat
✓ Révocation
✓ Vérification publique
```

---

# 45. Architecture globale

```text
                         SCHOOL ON

                           USER
                            │
                            ▼
                         COURSE
                            │
                     ┌──────┴──────┐
                     │             │
                  LESSONS        QUIZZES
                     │             │
                     └──────┬──────┘
                            │
                       PROGRESSION
                            │
                            ▼
                    CERTIFICATION ENGINE
                            │
             ┌──────────────┼──────────────┐
             │              │              │
        Completion       Quiz Score     Final Project
             │              │              │
             └──────────────┼──────────────┘
                            │
                     Mentor Approval
                            │
                            ▼
                       CERTIFICATE
                            │
              ┌─────────────┼─────────────┐
              │             │             │
             PDF           QR          Database
              │             │             │
              ▼             ▼             ▼
         Download       Verify       Certificate
         / Print        Online        History
```

---

# 46. Flux complet de l'apprenant

```text
1. L'utilisateur s'inscrit au cours
              ↓
2. Il commence les modules
              ↓
3. Il progresse
              ↓
4. Il réalise les quiz
              ↓
5. Les résultats sont enregistrés
              ↓
6. Il termine les contenus obligatoires
              ↓
7. Il réalise le projet final si nécessaire
              ↓
8. Le mentor évalue le projet si nécessaire
              ↓
9. Certification Engine vérifie les conditions
              ↓
10. Toutes les conditions sont satisfaites
              ↓
11. Certificate créé
              ↓
12. PDF généré
              ↓
13. QR Code généré
              ↓
14. Certificat disponible dans le dashboard
```

---

# 47. Flux avec validation mentor

```text
Apprenant termine le cours
          ↓
Toutes les conditions automatiques OK
          ↓
PENDING_MENTOR_APPROVAL
          ↓
Mentor reçoit notification
          ↓
Mentor vérifie
          ↓
[ APPROVE ]
          ↓
CERTIFICATE GENERATED
```

Si le mentor refuse :

```text
[ REJECT ]

Reason:
"Projet final incomplet"

          ↓

Certification bloquée
          ↓
Apprenant corrige le projet
          ↓
Nouvelle soumission
```

---

# 48. Notifications

Le système peut générer des notifications.

### Cours terminé

```text
Votre cours est terminé.
Il vous reste une étape pour obtenir votre certification.
```

### Certification en attente

```text
Votre certification est en attente de validation par votre mentor.
```

### Certificat disponible

```text
Félicitations !
Votre certificat School On est disponible.
```

### Certificat révoqué

```text
Votre certificat School On a été révoqué.
Consultez les détails dans votre espace.
```

---

# 49. Administration

L'administrateur doit pouvoir consulter :

```text
Admin
│
├── Certificates
│
├── Issued certificates
├── Pending certificates
├── Revoked certificates
└── Certificate verification
```

Filtres :

```text
Course
Mentor
Student
Date
Status
Certificate ID
```

---

# 50. Statistiques

Plus tard, l'administration pourra voir :

```text
Total certificates issued
Certificates this month
Certificates by course
Certificates by mentor
Revoked certificates
Certification success rate
```

Exemple :

```text
Certificats délivrés : 1,245

JavaScript       320
Python           285
UI/UX            190
Digital Marketing 170
Other            280
```

---

# 51. MVP recommandé

Pour la première version, ne pas essayer de construire toutes les fonctionnalités.

Le MVP doit contenir :

```text
✓ Course certifiant
✓ Conditions de réussite
✓ Progression
✓ Intégration avec quiz existants
✓ Validation finale
✓ Certificate model
✓ Certificate ID
✓ Signature mentor
✓ Signature School On
✓ Génération PDF
✓ QR Code
✓ Page de vérification
✓ Téléchargement
✓ Impression
✓ Dashboard "Mes certificats"
✓ Révocation admin
```

---

# 52. Fonctionnalités à ajouter plus tard

Après le MVP :

```text
→ LinkedIn sharing
→ WhatsApp sharing
→ Email certificate
→ Digital badges
→ Micro-credentials
→ Certificate categories
→ Certificate templates
→ Multiple certificate designs
→ Certificate analytics
→ Employer verification portal
→ Public learner portfolio
→ Skills profile
→ Blockchain / verifiable credentials
```

Ces éléments ne sont pas nécessaires pour commencer.

---

# 53. Règle importante sur la valeur du certificat

School On ne doit jamais présenter le certificat comme :

> "Une garantie d'emploi."

Le certificat signifie :

> **"Cette personne a satisfait les critères de réussite définis pour ce parcours School On."**

La valeur professionnelle du certificat augmentera avec :

```text
Qualité des cours
+
Qualité des évaluations
+
Qualité des projets
+
Qualité des mentors
+
Vérification
+
Réputation de School On
```

C'est pourquoi il faut éviter de délivrer un certificat simplement parce qu'un utilisateur a payé.

---

# 54. Résumé pour l'équipe Backend

Le backend doit construire le système autour de cette logique :

```text
COURSE
   ↓
ENROLLMENT
   ↓
PROGRESS
   ↓
QUIZ RESULTS
   ↓
FINAL ASSESSMENT / PROJECT
   ↓
CERTIFICATION ENGINE
   ↓
ELIGIBILITY
   ↓
MENTOR APPROVAL (si nécessaire)
   ↓
CERTIFICATE
   ↓
PDF + QR
   ↓
PUBLIC VERIFICATION
```

Le système de certification doit **réutiliser les modèles et fonctionnalités existants**, particulièrement :

* Course ;
* Enrollment ;
* Quiz ;
* QuizAttempt / résultats ;
* User ;
* Mentor ;
* Project / Final Assessment.

Il ne faut pas créer des systèmes parallèles qui dupliquent ces fonctionnalités.

---

# 55. Résumé pour l'équipe Frontend

Le frontend doit principalement gérer :

```text
Course certification information
        ↓
Certification progress
        ↓
Requirements checklist
        ↓
Certificate notification
        ↓
Certificate preview
        ↓
Download
        ↓
Print
        ↓
Share
```

Pour la vérification publique :

```text
/verify/:certificateId
```

Le frontend appelle le backend et affiche le résultat.

---

# 56. Principe final

Le système de certification School On doit suivre cette philosophie :

```text
        APPRENDRE
            ↓
        PRATIQUER
            ↓
        ÊTRE ÉVALUÉ
            ↓
        ÊTRE VALIDÉ
            ↓
        ÊTRE CERTIFIÉ
            ↓
        POUVOIR LE PROUVER
```

Le certificat n'est donc pas une décoration ajoutée à la fin d'un cours.

Il constitue la dernière étape du parcours d'apprentissage :

```text
COURSE
   +
QUIZ
   +
PRACTICE
   +
MENTOR
   +
ASSESSMENT
   ↓
CERTIFICATION SCHOOL ON
```

**Objectif final :**

> Transformer le certificat School On en une preuve vérifiable de compétences acquises et de parcours complété, plutôt qu'en simple document de participation.
