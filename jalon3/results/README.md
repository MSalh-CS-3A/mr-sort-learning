# Résultats du jalon 3

Les résultats de référence du rapport sont dans :

- `confirmation_quatre_couples_v1/` : 840 évaluations, vingt graines, trois
  tailles de A, deux attaques et deux défenses ;
- `analyse_approfondie_confirmation_v1/` : diagnostics des candidats, des
  groupes, des classes et des compromis de coût ;
- `recherche_selection_v1/` : développement du sélecteur hybride et transfert
  rétrospectif, explicitement exploratoire.

Les autres dossiers retracent les validations et campagnes préliminaires.
`calibrage_local_v1` contient le calibrage initial affecté par la conversion
des poids nuls : ses résultats ne sont pas utilisés comme confirmation.
`calibrage_local_v2` est sa relance après correction et fournit le corpus de
développement du sélecteur hybride.

Git conserve les mesures CSV, configurations, audits, bilans et figures. Les
archives brutes (`instances/`, `lots/`), copies figées du code (`sources/`),
journaux et dossiers de vérification du lanceur sont conservés localement et
exclus de Git. Certains chemins et empreintes des manifestes se réfèrent à ces
archives locales ; leur absence dans un clone ne signifie pas un audit échoué.

Un clone permet de consulter les résultats et de compiler le rapport avec les
figures fournies. Rejouer les audits depuis les modèles, reconstruire les
diagnostics ou régénérer les données du rapport nécessite les archives brutes
d'origine, ou de nouvelles campagnes avec le protocole documenté. Les arrêts
en temps réel ne garantissent pas des modèles identiques lors d'une relance.
