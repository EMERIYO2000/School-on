# SCHOOL ON --- Color System

## 1. Philosophy

La palette combine une base technologique bleue avec un accent
terracotta plus humain et chaleureux.

## 2. Core colors

  Token                     Hex         Usage
  ------------------------- ----------- -----------------------------------
  `brand.blue`              `#2563EB`   Actions principales, liens, focus
  `brand.blue-dark`         `#1E3A8A`   Titres accentués, éléments forts
  `brand.terracotta`        `#C96A4A`   Accent de marque, highlights
  `brand.terracotta-dark`   `#9F4F35`   Accent hover / contrasté
  `neutral.950`             `#0F172A`   Texte principal
  `neutral.700`             `#334155`   Texte secondaire
  `neutral.500`             `#64748B`   Texte muted
  `neutral.300`             `#CBD5E1`   Bordures
  `neutral.100`             `#F1F5F9`   Surfaces secondaires
  `neutral.50`              `#F8FAFC`   Background
  `white`                   `#FFFFFF`   Surfaces principales

## 3. Semantic colors

  Token       Usage
  ----------- -----------------------------
  `success`   succès, progression validée
  `warning`   attention, attente
  `error`     erreur, action destructive
  `info`      information neutre

Valeurs de référence :

-   Success: `#16A34A`
-   Warning: `#D97706`
-   Error: `#DC2626`
-   Info: `#0284C7`

## 4. Usage ratio

La majorité de l'interface doit rester neutre.

``` text
Neutrals       ████████████████████
Tech Blue      ████
Terracotta     ██
Semantic       █
```

Le terracotta est un accent, pas une couleur de fond omniprésente.

## 5. Accessibility

Ne jamais choisir une couleur uniquement parce qu'elle est visuellement
jolie.

Vérifier le contraste texte/fond.

Les états ne doivent jamais être communiqués uniquement par la couleur :
ajouter texte, icône ou autre indication.
