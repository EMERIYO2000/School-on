# SCHOOL ON --- UI States

## 1. Global states

Chaque fonctionnalité doit prévoir :

``` text
Default
Loading
Empty
Error
Success
Disabled
Pending
Unauthorized
Forbidden
```

## 2. Loading

Préférer :

-   skeleton pour les layouts de contenu
-   spinner pour une action ponctuelle
-   bouton loading pour une soumission

Éviter de bloquer toute la page lorsqu'une seule section charge.

## 3. Empty

Un empty state doit expliquer :

1.  ce qui manque
2.  pourquoi
3.  ce que l'utilisateur peut faire

Exemple de structure :

``` text
Illustration
Titre
Explication courte
Action principale
```

## 4. Error

Une erreur doit être :

-   compréhensible
-   proche de l'action concernée
-   non technique lorsque possible
-   accompagnée d'une action de récupération

Éviter d'afficher directement des messages backend bruts.

## 5. Forms

Erreur :

``` text
Label
Input
Message d'erreur
```

Le champ concerné doit être identifiable sans dépendre uniquement de la
couleur.

## 6. Pending states

Exemples :

-   vérification mentor en attente
-   réservation en attente
-   paiement en attente
-   certification en attente

Utiliser une combinaison :

-   badge
-   texte explicatif
-   prochaine action éventuelle

## 7. Security states

### Session expired

Message clair + reconnexion.

### Unauthorized

L'utilisateur n'est pas connecté ou sa session n'est plus valide.

### Forbidden

L'utilisateur est connecté mais n'a pas l'autorisation nécessaire.

Ne jamais exposer d'informations sensibles dans un écran d'erreur.

## 8. Destructive actions

Exemples :

-   supprimer un cours
-   annuler une réservation
-   supprimer un contenu

Demander confirmation lorsque l'action est difficilement réversible.

## 9. Accessibility

Les états doivent être compréhensibles :

-   visuellement
-   textuellement
-   au clavier
-   avec lecteur d'écran

Ne pas dépendre uniquement de la couleur, de l'animation ou de l'icône.
