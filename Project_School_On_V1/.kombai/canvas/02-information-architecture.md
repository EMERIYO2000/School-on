# SCHOOL ON --- Information Architecture

## 1. Public

``` text
/
├── about
├── privacy
├── terms
├── login
├── register
└── forgot-password
```

## 2. Learner

``` text
/dashboard

/courses
/courses/:id
/learning/:courseId
/learning/:courseId/chapter/:chapterId

/quiz
/quiz/:id
/quiz/:id/result

/exams
/exams/:id

/mentors
/mentors/:id

/bookings
/bookings/:id

/community

/certificates
/certificates/:id

/profile
/settings
```

## 3. Mentor

``` text
/mentor/dashboard

/mentor/courses
/mentor/courses/create
/mentor/courses/:id
/mentor/courses/:id/edit

/mentor/learners
/mentor/bookings
/mentor/earnings
/mentor/certificates

/mentor/profile
/mentor/verification
/mentor/settings
```

## 4. Admin

``` text
/admin/dashboard
/admin/users
/admin/mentors
/admin/courses
/admin/quizzes
/admin/exams
/admin/bookings
/admin/payments
/admin/certificates
/admin/reports
/admin/moderation
/admin/settings
```

## 5. Navigation model

### Desktop

``` text
┌──────────────┬──────────────────────────────┐
│ Sidebar      │ Main content                 │
│              │                              │
│ Navigation   │ Page header                  │
│              │                              │
│              │ Main workspace               │
└──────────────┴──────────────────────────────┘
```

### Mobile

``` text
┌──────────────────────┐
│ Header               │
├──────────────────────┤
│ Main content         │
│                      │
│                      │
├──────────────────────┤
│ Bottom navigation    │
└──────────────────────┘
```

La navigation mobile ne doit pas reproduire mécaniquement la sidebar
desktop.

## 6. Information hierarchy

Priorité générale :

1.  Contexte de la page
2.  Action principale
3.  Informations essentielles
4.  Actions secondaires
5.  Informations avancées

## 7. Cross-navigation

Les entités doivent être reliées visuellement :

``` text
Cours
 ├── Mentor
 ├── Progression
 ├── Quiz
 └── Certification

Mentor
 ├── Profil
 ├── Cours
 └── Réservations

Apprenant
 ├── Cours
 ├── Quiz
 ├── Mentors
 └── Certificats
```

## 8. API boundary

Ce document ne définit pas :

-   endpoints
-   payloads
-   authentification technique
-   modèles backend
-   webhooks
-   logique serveur

Ces éléments appartiennent à la documentation backend/API.
