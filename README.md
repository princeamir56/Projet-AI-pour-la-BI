# Projet AI pour la BI — Maintenance industrielle (ERP)

> **5ᵉ année Génie Informatique BI — Année universitaire 2026-2027**
> Module *AI pour la BI*, encadré par Dr. Ing. Rihab LAAJILI

Ce document est la **documentation complète du projet**. Les notebooks contiennent le code et les titres de section. Le contexte, les constats, les décisions et leurs justifications, les résultats et les limites sont rassemblés ici.

---

## Sommaire

- [Avancement du projet](#avancement-du-projet)
- [Structure du dépôt](#structure-du-dépôt)
- [Reproduire les résultats](#reproduire-les-résultats)
- [Contexte et objectifs](#contexte-et-objectifs)
- [Partie 1 — Data Preparation & Feature Engineering](#partie-1--data-preparation--feature-engineering)
  - [Étape 1 — Compréhension et exploration](#étape-1--compréhension-et-exploration-des-données)
  - [Étape 2 — Audit de qualité](#étape-2--évaluation-de-la-qualité-des-données)
  - [Étape 3 — Nettoyage et préparation](#étape-3--nettoyage-et-préparation)
  - [Étape 4 — Intégration (jointures)](#étape-4--intégration-des-données)
  - [Étape 5 — Feature Engineering](#étape-5--feature-engineering)
  - [Étape 6 — Data Leakage](#étape-6--data-leakage)
  - [Étape 7 — Synthèse, datasets produits, limites](#étape-7--synthèse)
- [Partie 2 — Supervised Learning](#partie-2--supervised-learning)
- [Partie 3 — Unsupervised Learning](#partie-3--unsupervised-learning)

---

## Avancement du projet

| Partie | Sujet | Statut |
|---|---|---|
| **Partie 1** | Data Preparation & Feature Engineering | ✅ Terminée |
| **Partie 2** | Supervised Learning | ⏳ Pas encore commencée |
| **Partie 3** | Unsupervised Learning | ⏳ Pas encore commencée |

---

## Structure du dépôt

```
AiPourBI/
├── README.md                     <- cette documentation
├── docs/
│   └── cahierdecharge.pdf        <- cahier des charges du projet
├── data/
│   ├── fichiers principaux/      <- 13 CSV de l'ERP + 2 documentations (.docx)
│   └── annexe/                   <- 11 CSV facultatifs
├── Partie1/
│   ├── Partie1_Data_Preparation_Feature_Engineering.ipynb
│   └── outputs/                  <- datasets nettoyés, features, audit, journal (CSV)
└── Partie2/                      <- (à venir)
```

## Reproduire les résultats

- **Environnement :** Python 3.12, pandas 2.3, numpy, matplotlib, seaborn, jupyter.
- **Exécution :** ouvrir `Partie1/Partie1_Data_Preparation_Feature_Engineering.ipynb` et exécuter toutes les cellules dans l'ordre.
  - En ligne de commande : `jupyter nbconvert --to notebook --execute --inplace Partie1/Partie1_Data_Preparation_Feature_Engineering.ipynb`
  - Les chemins sont relatifs : le notebook lit `../data/` et écrit dans `Partie1/outputs/`.
  - Une graine aléatoire fixe (`SEED = 42`) est définie, bien que la Partie 1 ne comporte aucune étape aléatoire.
- **Garanties :**
  - Les données brutes ne sont **jamais modifiées**. Chaque transformation crée une nouvelle table et est inscrite dans un journal (`journal_transformations.csv`).
  - **Aucune donnée externe** n'est utilisée, conformément au cahier des charges.

---

## Contexte et objectifs

Les données proviennent d'un **ERP réel de gestion de la maintenance industrielle** d'un atelier de confection : machines à coudre, de coupe, à souder, etc. Elles sont réparties dans plusieurs fichiers CSV liés entre eux :

- les machines ;
- les réparations et les appels de panne ;
- les entretiens préventifs et leur planification ;
- les emplacements ;
- les référentiels (natures de panne, problèmes, actions, catégories).

L'objectif n'est pas seulement d'entraîner un modèle. Il s'agit de mener une **démarche data complète et argumentée** :

> **Comprendre → Préparer → Construire → Justifier → Modéliser → Évaluer → Interpréter → Critiquer**

Les trois parties du projet :
1. **Partie 1 :** préparation des données et feature engineering. Cette partie est commune à tous les groupes.
2. **Partie 2 :** apprentissage supervisé. Sujet à choisir parmi :
   - **S1** — prédire une panne future ;
   - **S2** — prédire le nombre de réparations futures ;
   - **S3** — prédire la durée ou la gravité d'une réparation.
3. **Partie 3 :** apprentissage non supervisé. Sujet à choisir parmi :
   - **U1** — segmenter les machines selon leur profil de fiabilité ;
   - **U2** — segmenter les machines selon leur profil de maintenance ;
   - **U3** — détecter les machines atypiques.

---

# Partie 1 — Data Preparation & Feature Engineering

**Question centrale :** *Dans quel état avons-nous reçu les données, et comment les avons-nous transformées pour qu'elles deviennent exploitables ?*

**Notebook :** [`Partie1/Partie1_Data_Preparation_Feature_Engineering.ipynb`](Partie1/Partie1_Data_Preparation_Feature_Engineering.ipynb). Les numéros de section ci-dessous correspondent aux titres du notebook.

## Résumé exécutif

- Le dataset est un **ERP relationnel de 13 tables**. Son **intégrité référentielle est parfaite** : aucune clé orpheline.
- La **qualité du contenu est inégale** :
  - 43 colonnes sont vides ou constantes ;
  - une table entière est en doublon (`mouvement`) ;
  - environ 15 % des durées sont incohérentes entre elles ;
  - des planifications futures sont mélangées aux observations ;
  - certains champs cumulés provoquent une **fuite de données**.
- Constats démontrés par les données :
  - les **durées sont en minutes** ;
  - la **date d'extraction est le 5 mars 2026** ;
  - des **interventions multiples sur un même arrêt** ont été mises au jour.
- Résultats produits :
  - un dataset **événementiel** de 32 772 réparations décodées ;
  - un dataset **machine × date T** de 1 649 machines et environ 35 features documentées ;
  - une **fonction de construction des features sans fuite**, vérifiée par un test automatique et réutilisable pour les Parties 2 et 3.

---

## Étape 1 — Compréhension et exploration des données

### 1.1 Inventaire des fichiers

| Table | Fichier | Lignes | Colonnes | Colonnes 100 % vides | % manquant global | Rôle |
|---|---|---:|---:|---:|---:|---|
| machine | `gm_machineinstance.csv` | 1 649 | 42 | 8 | 30,8 | Référentiel machines (**table pivot**) |
| reparation | `gm_reparation.csv` | 32 772 | 42 | 3 | 33,1 | Interventions correctives |
| appel | `gm_reparationappel.csv` | 32 331 | 14 | 4 | 28,8 | Signalements de panne |
| entretien | `gm_entretien.csv` | 65 173 | 18 | 2 | 23,2 | Occurrences de maintenance préventive |
| preventif | `gm_preventif_machine.csv` | 4 109 | 16 | 5 | 47,8 | Configuration du préventif (machine × action) |
| historique | `gm_historiquemachineendroit.csv` | 15 191 | 7 | 2 | 28,6 | Emplacements datés |
| mouvement | `gm_mouvementmachine.csv` | 15 191 | 6 | 0 | 16,5 | Mouvements, sans date |
| action | `gm_action.csv` | 62 | 5 | 2 | 40,0 | Référentiel des actions |
| nature | `gm_naturepanne.csv` | 40 | 3 | 0 | 4,2 | Référentiel des natures d'intervention |
| probleme | `gm_problemepanne.csv` | 32 | 3 | 0 | 0,0 | Référentiel des problèmes constatés |
| classe | `gm_classemachine.csv` | 417 | 5 | 0 | 19,1 | Modèles de machines |
| categorie | `gm_categoriemachine.csv` | 11 | 2 | 0 | 0,0 | Catégories de machines |
| endroit | `gm_endroitmachine.csv` | 68 | 8 | 0 | — | Emplacements : lignes, parcs, ateliers |

**Lecture**
- Le volume vient de trois tables d'événements : `entretien`, `reparation` et `appel`. Les autres tables sont des référentiels ou des historiques.
- **Aucun doublon exact** n'existe dans les fichiers.
- En revanche, **plusieurs tables contiennent des colonnes entièrement vides**. C'est typique d'un export ERP : le schéma est générique et le client n'utilise qu'une partie des champs.

**Fichiers annexes (11 fichiers, facultatifs).** Ils sont **exclus du périmètre analytique** pour trois raisons :
- leur contenu est déjà présent sous forme de libellé dans les fichiers principaux (`gm_etatmachine` → `machine.etat`, `gm_moteurmachine` → `machine.moteur`) ;
- certains sont trop peu remplis : `gm_piecereparation` contient 22 lignes pour plus de 32 000 réparations, et `gm_entreemagasinpiece.machine_instance` est vide à 100 % ;
- les autres sont peu reliés aux machines.

Le cahier des charges le rappelle : l'objectif n'est pas d'utiliser le maximum de fichiers.

### 1.2 Structure détaillée

Le notebook présente un profil colonne par colonne de chaque table : type, nombre de valeurs non nulles, % manquant, cardinalité et modalité dominante. Les points marquants sont détaillés dans les sections suivantes.

### 1.3 Granularité : que représente une ligne ?

Toutes les clés primaires ont été vérifiées par le code : elles sont **uniques et non nulles**. Dans `preventif`, le couple *(machine, action)* est également unique.

| Table | Clé | Une ligne = |
|---|---|---|
| machine | `id_machine_instance` | une machine physique du parc, dans son état au moment de l'extraction |
| reparation | `id_reparation` | une intervention corrective : arrêt → prise en charge → fin |
| appel | `id_appel` | un signalement de panne émis par la production, qui précède la réparation |
| entretien | `id_entretien` | une occurrence d'action préventive sur une machine |
| preventif | `id` | un couple (machine, action) avec sa fréquence et ses dernière et prochaine échéances |
| historique | `id_historique_endroit` | une lecture datée de l'emplacement d'une machine |
| mouvement | `id` | un déplacement (origine → destination), **sans date** |
| référentiels | `id_*` | un libellé : action, nature, problème, classe, catégorie, emplacement |

### 1.4 Clés et relations

```
                      categorie (11)   classe (417)   endroit (68)
                            ^               ^             ^
                            |  N-1          |  N-1        |  N-1
                            +---------  MACHINE (1 649)  -+          <- table pivot
                                            ^
       +---------------+--------------------+--------------+------------------+
       | N-1           | N-1                | N-1          | N-1              | N-1
  REPARATION <-1-1-  APPEL            ENTRETIEN        PREVENTIF        HISTORIQUE (= MOUVEMENT)
   |       |                               |                |
 nature  probleme                        action <-----------+
```

| Relation | Correspondance | Cardinalité | Couverture de la cible |
|---|---:|---|---:|
| reparation → machine | 100 % | N–1 (max 185 réparations par machine) | 80,0 % des machines |
| entretien → machine | 100 % | N–1 (max 1 134) | 80,7 % |
| historique → machine | 100 % | N–1 (max 48) | 93,8 % |
| preventif → machine | 100 % | N–1 (max 3) | 86,1 % |
| appel → reparation | 100 % | **1–1** | 97,4 % des réparations |
| reparation → nature / probleme / endroit | 100 % | N–1 | — |
| machine → classe / categorie / endroit | 100 % | N–1 | — |

**Lecture**
- **Aucune clé orpheline** n'existe : l'intégrité référentielle est parfaite.
- Toutes les tables d'événements sont en relation **N–1** avec la machine. C'est ce qui crée le risque de duplication lors des jointures (voir l'étape 4).
- `appel → reparation` est en relation **1–1** : cette jointure ne duplique aucune ligne.
- Environ **20 % des machines n'ont aucun événement** : machines récentes, stockées au parc ou inactives.
- `reparation.id_endroit` désigne la **ligne de production** au moment de la panne (MF1, ZS8, E2…).

### 1.5 Périodes temporelles

| Champ | Plage observée |
|---|---|
| `machine.date_achat` | 1994-11-26 → 2026-02-10 |
| `reparation.datearretchaine` | 2021-11-13 → 2026-03-05 |
| `appel.date_appel` | 2021-11-13 → 2026-03-05 |
| `entretien.date_debut` | 2020-01-03 → **2026-07-17** |
| `entretien.date_prevue` | 2016-06-09 → **2027-02-11** |
| `preventif.prochain_entretien_jour` | 2022-12-23 → **2027-02-12** |
| `historique.date_lecture` | 2019-07-10 → 2026-03-05 |

**Lecture**
- **Date d'extraction retenue : 2026-03-05.** C'est la date du dernier événement réellement observé (arrêt, appel ou lecture d'emplacement). Les dates postérieures correspondent à de la **planification**, pas à des observations.
- Les événements commencent fin 2021 pour les réparations et mi-2022 pour les entretiens, ce qui correspond à la **montée en charge de l'ERP**. Les dates patrimoniales remontent à 1994.
- Une **saisonnalité nette** apparaît : creux chaque mois d'**août**, qui correspond aux congés industriels. Le creux de **mars 2026** s'explique par un mois incomplet (extraction le 5 mars).
- `dateheurerep` et `datefin` mélangent deux formats (avec et sans millisecondes). C'est ce qui expliquait l'écart, dans la documentation, sur le nombre de valeurs valides. Une lecture au format ISO 8601 rend **plus de 99 % des valeurs exploitables**.

### 1.6 Variables et unité des durées

**Types de variables**
- **Quantitatives :** durées de réparation, d'arrêt et d'attente ; durée et arrêt d'entretien ; fréquence préventive ; coûts.
- **Catégorielles :** état, catégorie, fabricant, méthode, moteur, catégorie de réparation, indicateurs t/f.
- **Dates :** voir la section 1.5.
- Les identifiants `id_*` sont des **clés** et ne sont jamais traités comme des nombres.

**Unité des durées : démontrée à partir des données.** Aucune unité n'était documentée. Nous avons recalculé, en minutes, l'écart entre les horodatages qui encadrent chaque durée :

| Hypothèse (en minutes) | Concordance à ±2 min |
|---|---:|
| `dureeattente` ≈ `dateheurerep − datearretchaine` | 86,7 % |
| `dureerep` ≈ `datefinmecanicien − dateheurerep` | 91,9 % |
| `dureearret` ≈ `datefin − datearretchaine` | 86,5 % |

**Les durées de réparation sont exprimées en minutes.** Le cycle d'une réparation est le suivant : **arrêt → attente → prise en charge par le mécanicien → réparation → fin**, et on a généralement `dureearret ≈ dureeattente + dureerep`.

**Distributions**
- Durée d'arrêt : médiane de 12 min et 99ᵉ centile de 155 min. La distribution est très asymétrique, avec une longue traîne.
- Il existe aussi des valeurs **négatives**, impossibles, et quelques valeurs supérieures à 8 h.
- Nombre de réparations par machine (parmi les machines réparées) : médiane de 15, maximum de 185.
- **Les 10 % de machines les plus touchées concentrent 36,6 % des réparations.**
- Problèmes les plus fréquents : *mauvais aspect, point sauté, casse fil*.
- Natures les plus fréquentes : *réglage point, réglage machine, PANNE NON ELIGIBLE*. Cette dernière correspond probablement à des interventions qui ne sont pas imputables à la machine.
- Le parc compte **87 % de machines à coudre**. Les autres catégories sont minoritaires et devront être regroupées.

### 1.7 Variables quasi constantes

**43 colonnes** sont vides ou quasi constantes. Les plus notables :
- `machine.vendu` vaut `f` partout ;
- `entretien.faite` vaut `f` dans 65 172 lignes sur 65 173. L'indicateur n'est donc **pas utilisé par l'ERP**, et on ne peut pas distinguer un entretien réalisé d'un entretien planifié ;
- `reparation.nombre_piece` vaut toujours 0 ;
- `reparation.type` vaut « Atelier » dans 99,4 % des cas ;
- `appel.cloture` vaut `t` partout ;
- `historique.actif` vaut `f` partout.

### 1.8 Redondances

| Redondance | Concordance | Décision |
|---|---:|---|
| `daterep` = partie date de `dateheurerep` | 100 % | supprimer `daterep` |
| `datearretchaine_withouthour` = date de `datearretchaine` | 98,8 % | supprimer (dérivable) |
| `duree_attente` (82 % NA) vs `dureeattente` | 84,7 % | garder `dureeattente`, renseignée à 98 % |
| `reparation.nom_machine` vs `machine.nom_machine` | 97,3 % | supprimer : l'information vient de la jointure |
| `machine.type` = libellé de catégorie | 100 % | supprimer : repris via `categorie` |
| `machine.fabricant` = `classe.fabricant` | 99,9 % | n'en garder qu'une |
| `machine.nom_machine` vs `classe.desigantion` | 90,0 % | désignation reprise via `classe` |
| `date_declaration` vs `date_achat` | 91,7 % | garder `date_achat`, complète à 100 % ; `date_declaration` est manquante à 36 % |
| problème de l'appel = problème de la réparation | 100 % | l'appel sert de déclencheur ; seul le délai de prise en charge est conservé |
| `date_appel` ≈ date d'arrêt (à 1 min près) | 93,0 % | idem |
| **`mouvement` = `historique`** (mêmes machines et destinations, identifiant décalé de 1) | 100 % | **la table `mouvement` est écartée** : même information, sans date |

---

## Étape 2 — Évaluation de la qualité des données

Chaque problème est **chiffré** et associé à une **décision justifiée**. Le tableau complet est exporté dans [`Partie1/outputs/audit_qualite.csv`](Partie1/outputs/audit_qualite.csv).

| Table | Problème | Nb | % | Décision |
|---|---|---:|---:|---|
| toutes | colonnes vides (≥ 99,5 % NA) | 31 col. | — | supprimer : aucune information |
| machine | `cout` (93 % NA), `remarque` (98 % NA) | 2 col. | — | supprimer : trop peu renseignées |
| reparation | `id_produit`, `id_sousfamille`, `id_client`, `designation_process` (~89 % NA) | 4 col. | — | supprimer : champs d'un autre module |
| reparation | doublons exacts | 0 | 0 | — |
| reparation | lignes partageant *(machine, date d'arrêt)* avec une autre | 1 026 | 3,13 | **conserver** : plusieurs interventions sur un même arrêt (voir 3.3) |
| entretien | doublons logiques (machine, action, même date-heure) | 1 267 | 1,94 | supprimer : double saisie |
| historique | doublons logiques (machine, date, emplacement) | 537 | 3,53 | supprimer : lecture répétée |
| reparation | `dureearret` / `dureerep` / `dureeattente` négatives | 66 / 36 / 24 | 0,2 / 0,1 / 0,1 | mettre à NaN : durée impossible |
| reparation | `dureearret` manquante | 178 | 0,54 | reconstruire par attente + réparation quand c'est possible (1 seul cas) |
| reparation | arrêt > 480 min (plus d'un poste de travail) | 10 | 0,03 | conserver avec un drapeau : arrêts longs plausibles |
| reparation | écart de plus de 2 min entre attente + réparation et arrêt | 4 907 | 14,97 | conserver : saisies a posteriori ; la durée d'arrêt sert de référence |
| reparation | `datefin` antérieure à `datearretchaine` | 30 | 0,09 | drapeau |
| reparation | `datefin` plus d'un jour après l'arrêt | 1 165 | 3,55 | drapeau : il s'agit d'une clôture administrative, pas de la fin réelle |
| reparation | réparation non clôturée | 4 126 | 12,59 | conserver, avec une variable binaire |
| reparation | réparation antérieure à l'achat de la machine | 1 | 0,00 | conserver : date d'achat douteuse |
| entretien | date postérieure à l'extraction (planification) | 7 | 0,01 | **supprimer** : entretien non observé |
| entretien | entretien antérieur à l'achat de la machine | 84 | 0,13 | conserver : date d'achat douteuse |
| entretien | écart de plus de 365 j entre date réelle et date prévue | 133 | 0,20 | retard mis à NaN : planification incohérente |
| machine | coûts cumulés négatifs | 205 | 12,43 | supprimer les coûts (incohérents et source de fuite) |
| machine | `date_declaration` antérieure à `date_achat` | 8 | 0,49 | sans impact : colonne non retenue |
| reparation | `categorie_reparation` : casse incohérente et modalités rares | 331 | 1,01 | harmoniser et regrouper en « Autre » |
| machine | `fabricant` / `nom_machine` : variantes de casse ou d'espaces | 11 / 16 | — | normaliser (majuscules, espaces) |
| endroit | `nature` : « Production » / « PRODUCTION » / « Hors Production  » | 3 | — | normaliser |
| probleme | même libellé (« purgeur d'air ») sous 3 identifiants | 3 | — | conserver les identifiants, harmoniser le libellé |
| toutes | clés étrangères orphelines | 0 | 0 | aucune action |
| appel | appel sans réparation associée | 425 | 1,31 | conserver dans la table appel |
| machine | machine sans aucune réparation | 330 | 20,01 | conserver : `nb_rep = 0` est une information |
| machine | `moteur` manquant | 384 | 23,29 | modalité « INCONNU » : l'absence peut être informative |
| reparation | nature ou problème manquant | 182 | 0,56 | modalité « INCONNU » |

**Synthèse de l'audit**
1. **Les clés sont bonnes, le contenu l'est moins.** L'intégrité est parfaite, mais plus d'un quart des colonnes ne porte aucune information.
2. **Les durées de réparation sont globalement fiables** : elles sont cohérentes avec les horodatages et leur unité est démontrée. En revanche, **`datefin` correspond souvent à une clôture administrative** et ne doit pas servir à calculer une durée.
3. **La table d'entretiens mélange observation et planification** : dates futures, indicateur `faite` inutilisable, doublons de saisie. C'est le principal point de vigilance pour la fuite de données.
4. **Plusieurs champs de `machine` sont des instantanés à la date d'extraction** (état, emplacement courant, coûts cumulés). Voir l'étape 6.
5. **Aucune valeur n'est supprimée seulement parce qu'elle est extrême.** Seules les valeurs **impossibles** sont neutralisées ; les valeurs extrêmes sont signalées par un drapeau.

---

## Étape 3 — Nettoyage et préparation

Toutes les opérations sont tracées dans [`journal_transformations.csv`](Partie1/outputs/journal_transformations.csv), soit 41 opérations justifiées.

### 3.1 Référentiels
- **`probleme`** : `id_naturepanne` / `lib_naturepanne` ont été renommés en `id_probleme` / `lib_probleme`. Ces noms étaient hérités d'un schéma générique, alors que le contenu décrit des **problèmes**.
- **`nature`, `probleme`, `classe`, `categorie`** : libellés normalisés (majuscules, espaces) ; `classe.description` supprimée (95 % NA).
- **`action`** : création d'une variable `famille_action`, égale au préfixe du libellé (M.C, C.A, MG, TR…). Elle regroupe 62 libellés très longs en familles lisibles.
- **`endroit`** : `nature` normalisée et regroupée dans `type_endroit` (PRODUCTION, PARC, HORS PRODUCTION, COUPE, DEVELOPPEMENT, AUTRE). Les indicateurs t/f sont convertis en 1/0.

### 3.2 Machines (42 → 20 colonnes)

| Colonnes supprimées | Raison |
|---|---|
| 8 colonnes 100 % vides | aucune information |
| `vendu` | constante |
| `cout_total`, `cout_reparation`, `cout_entretien` | **fuite de données** (cumuls incluant le futur) + valeurs négatives + 55 % de zéros |
| `cout`, `remarque` | 93 % / 98 % manquants |
| `type`, `classe`, `chaine`, `id_moteur`, `id_etat_machine`, `nom_machine` | redondantes : libellés repris via les jointures |
| `date_declaration`, `declaration`, `imm_unique`, `numero`, `id_machine_methode`, `id_site_*` (4 variantes) | identifiants techniques ou variantes de site ambiguës ; `date_achat` est la date de référence |

Autres traitements :
- normalisation de `fabricant`, `moteur`, `etat` et `nom_methode` ; les valeurs manquantes deviennent la modalité **« INCONNU »**, sans imputation arbitraire ;
- décodage de la catégorie et de la désignation de classe par des jointures N–1, avec vérification du nombre de lignes.

### 3.3 Réparations (42 → 21 colonnes, 32 772 lignes conservées)

- **Colonnes supprimées** : celles qui sont vides, redondantes (section 1.8), manquantes à plus de 89 %, constantes, ou qui correspondent à des identifiants de personnel hors sujet.
- **Renommage** : `date_arret`, `date_prise_en_charge`, `date_fin_intervention`, `date_cloture`, `duree_arret_min`, `duree_rep_min`, `duree_attente_min`, `id_nature`, `id_ligne`.
- **Types** : dates converties au format ISO 8601 ; indicateurs t/f convertis en 1/0.
- **Durées** :
  - les valeurs négatives sont mises à NaN (66 + 36 + 24) ;
  - une durée d'arrêt manquante est reconstruite par *attente + réparation* quand ces deux valeurs existent (1 cas).
- **Drapeaux** :
  - `flag_arret_long` : arrêt de plus de 480 min ;
  - `flag_date_cloture_incoherente` : clôture avant l'arrêt, ou plus d'un jour après.
- **`categorie_reparation`** : la casse est harmonisée et les modalités rares sont regroupées en « Autre » (9 → 6 modalités).
- **Pseudo-doublons (décision importante).** 1 026 lignes partagent la même machine et le même horodatage d'arrêt. L'examen montre qu'elles ont **des natures, des heures de fin et des durées différentes**. Exemple : une première intervention non clôturée est suivie d'une seconde. Ce sont donc **plusieurs interventions sur un même arrêt**, et non une double saisie.
  - Elles sont **conservées**.
  - Elles sont signalées par `nb_interventions_arret` et `intervention_multiple`.
  - Les features distinguent le nombre d'interventions (`nb_rep_total`) du nombre de pannes réelles (`nb_arrets_distincts`).

### 3.4 Appels (14 → 8 colonnes)
- Suppression des colonnes vides, de `cloture` (constante), du matricule et de l'emplacement (déjà présent dans la réparation).
- Création de `delai_consultation_min` (`date_consult − date_appel`), qui mesure la réactivité de la prise en charge. Médiane : 5,3 min.

### 3.5 Entretiens (65 173 → 63 899 lignes, 18 → 12 colonnes)
- Colonnes supprimées : `heuresactuelles` et `moisactuels` (5 valeurs chacune), les champs de planning (vides) et `faite` (inutilisable).
- **Suppression de 7 entretiens postérieurs à l'extraction** : ce sont des planifications.
- **Suppression de 1 267 doublons** (même machine, même action, même date-heure).
- Création de `retard_jours` (date réelle − date prévue). Les écarts de plus de 365 jours sont mis à NaN (127 lignes).
- Ajout de la variable `famille_action`.

### 3.6 Préventif et historique
- **`preventif`** : suppression des colonnes vides ou manquantes à plus de 95 % ; conversion des dates. Ce fichier est un **instantané** de la configuration (voir l'étape 6).
- **`historique`** : suppression des colonnes vides ou constantes et de **537 lectures en double**.
- **`mouvement`** : table écartée (doublon de `historique`, sans date).

---

## Étape 4 — Intégration des données

Toutes les jointures passent par une fonction de contrôle, `merge_controle`, qui :
- impose la cardinalité attendue (`validate='m:1'` ou `'1:1'`) ;
- vérifie que le **nombre de lignes reste inchangé** ;
- affiche le taux de correspondance.

### 4.1 Dataset « réparations enrichies » (une ligne = une réparation)

| Jointure | Type | Lignes avant → après | Correspondance |
|---|---|---|---:|
| réparation × nature | N–1 | 32 772 → 32 772 | 99,4 % |
| réparation × problème | N–1 | 32 772 → 32 772 | 99,4 % |
| réparation × ligne (endroit) | N–1 | 32 772 → 32 772 | ≈ 100 % |
| réparation × machine | N–1 | 32 772 → 32 772 | 100 % |
| réparation × appel | **1–1** | 32 772 → 32 772 | ≈ 98 % |

Les taux de correspondance inférieurs à 100 % viennent de clés **nulles** (nature ou problème absents, réparations sans appel). Il ne s'agit pas de clés orphelines.

Variables ajoutées :
- `age_machine_jours` : âge de la machine à la date de l'arrêt ;
- `flag_avant_achat` : réparation datée avant l'achat ;
- `heure_arret`, `jour_semaine`, `mois` : calendrier de l'arrêt.

### 4.2 Pourquoi on ne joint pas les tables d'événements entre elles

Joindre directement réparations et entretiens sur `id_machine_instance` produit une jointure **N–N** : **1,69 million de lignes**, soit 52 fois le nombre de réparations. Une même réparation apparaît jusqu'à 685 fois. Les moyennes deviendraient fausses et un modèle verrait des lignes dupliquées.

**La bonne démarche :** agréger chaque table d'événements au niveau **(machine, date T)**, puis joindre ces agrégats en **1–1**. C'est l'objet de l'étape 5.

---

## Étape 5 — Feature Engineering

### 5.1 Unité d'analyse et règle temporelle
- **Une observation = (machine, date d'observation T).** Cette représentation est commune aux sujets S1, S2, U1, U2 et U3.
- **Règle anti-fuite :** une feature calculée à T n'utilise **que des événements strictement antérieurs à T**.
- Les informations instantanées de l'ERP (état actuel, configuration du préventif) ne sont ajoutées **que si T est postérieure ou égale à la date d'extraction**.
- La fonction `build_machine_snapshot(T)` est **réutilisable**. En Partie 2, il suffira de l'appeler pour plusieurs dates T afin de construire un échantillon temporel. Le notebook en fait la démonstration avec 6 dates mensuelles, soit 9 621 lignes (machine × T).

### 5.2 Regroupement des catégories rares

Les regroupements sont calculés sur le référentiel des machines, **sans utiliser de cible**. Ils n'introduisent donc pas de fuite.

| Variable source | Modalités | Variable regroupée | Modalités |
|---|---:|---|---:|
| `fabricant` | 115 | `fabricant_grp` (8 principales + AUTRE) | 9 |
| `categorie_machine` | 12 | `categorie_grp` (≥ 30 machines, sinon AUTRE) | 5 |
| `designation_classe` | 104 | `designation_grp` (12 principales + AUTRE) | 13 |
| `nom_methode` | 32 | `methode_grp` (10 principales + AUTRE) | 11 |

### 5.3–5.4 Dictionnaire des features

Format : *nom → variables sources → méthode de calcul → signification → justification*. Le dictionnaire est exporté dans [`dictionnaire_features.csv`](Partie1/outputs/dictionnaire_features.csv).

| Feature | Sources | Calcul | Signification | Justification |
|---|---|---|---|---|
| `age_jours` | machine.date_achat | T − date_achat | âge de la machine | l'usure augmente avec l'âge |
| `exposition_jours` | date_achat, début des données | T − max(date_achat, début de l'historique) | durée observable | normalise les comptages |
| `nb_rep_total` | reparation | nombre de réparations avant T | volume d'interventions | indicateur principal de fiabilité |
| `nb_arrets_distincts` | reparation.date_arret | nombre d'arrêts distincts avant T | nombre de pannes réelles | un arrêt peut entraîner plusieurs interventions |
| `nb_rep_30j / 90j / 180j` | reparation.date_arret | comptage sur la fenêtre [T−w ; T[ | activité récente | le passé récent prédit mieux le futur proche |
| `tendance_rep` | nb_rep_30j, nb_rep_180j | (nb_30j + 1) / (nb_180j / 6 + 1) | accélération (> 1) ou ralentissement (< 1) | détecte une dégradation récente |
| `freq_rep_mensuelle` | nb_rep_total, exposition | nb_rep_total / (exposition / 30,44) | pannes par mois | comparable entre machines d'âges différents |
| `jours_depuis_derniere_rep` | reparation.date_arret | T − dernière date d'arrêt ; censuré à l'exposition | récence de la dernière panne | une panne récente annonce souvent une récidive |
| `duree_arret_moy / totale` | duree_arret_min | moyenne / somme | gravité moyenne et cumulée | distingue « fréquent et court » de « rare et long » |
| `duree_rep_moy` | duree_rep_min | moyenne | complexité technique | temps effectif du mécanicien |
| `duree_attente_moy` | duree_attente_min | moyenne | délai avant prise en charge | reflète l'organisation de la maintenance |
| `nb_arrets_longs` | flag_arret_long | somme | nombre d'arrêts majeurs | pannes graves |
| `nb_problemes_distincts / nb_natures_distinctes` | id_probleme, id_nature | nombre de valeurs distinctes | diversité des pannes | une machine aux problèmes variés est dégradée |
| `taux_rep_avec_changement` | changement | moyenne | part des réparations avec changement | signale des réparations lourdes |
| `nb_ent_total / nb_ent_90j` | entretien | comptage avant T / sur 90 j | intensité du préventif | le préventif est censé réduire les pannes |
| `jours_depuis_dernier_ent` | entretien.date_debut | T − dernier entretien ; censuré | récence de l'entretien | un entretien ancien augmente le risque |
| `retard_ent_moy_jours` | date_debut, date_prevue | moyenne des retards | respect du planning | des retards répétés traduisent une maintenance négligée |
| `nb_actions_ent_distinctes` | entretien.id_action | nombre de valeurs distinctes | diversité des actions préventives | profil de maintenance |
| `duree_ent_totale` | entretien.duree | somme | effort préventif cumulé | profil de maintenance (U2) |
| `ratio_prev_corr` | nb_ent, nb_rep | nb_ent / (nb_rep + 1) | équilibre préventif / correctif | demandé pour U2 / U3 |
| `nb_changements_emplacement` | historique | nombre de changements successifs d'emplacement | mobilité | les déplacements peuvent dérégler une machine |
| `type_endroit_T` | historique + endroit | emplacement à la dernière lecture avant T | production, parc, etc. | une machine au parc ne tombe pas en panne en production |
| `jamais_reparee / jamais_entretenue` | comptages | indicateur « = 0 » | absence d'historique | distingue « 0 » de « inconnu » |
| `categorie_grp`, `fabricant_grp`, `designation_grp`, `methode_grp`, `moteur` | machine + référentiels | modalités rares regroupées | caractéristiques techniques | le comportement varie selon le type et la marque |
| `etat_actuel`, `freq_prev_min_jours`, `nb_actions_prev_planifiees` | machine.etat, preventif | valeur à l'extraction (**seulement si T ≥ extraction**) | configuration actuelle | utile en non supervisé ; exclu pour un T passé (fuite) |

**Valeurs pour les machines sans événement :**
- les comptages valent **0** : c'est l'absence d'événement, et non une donnée manquante ;
- les temps écoulés sont **censurés à la durée d'exposition** ;
- les indicateurs `jamais_reparee` et `jamais_entretenue` gardent la trace de cette situation.

### 5.5 Analyse des features (snapshot à T = 2026-03-06, 1 649 machines)

**Statistiques descriptives**
- `nb_rep_total` : médiane de 10 et maximum de 185 ; 20 % des machines n'ont jamais été réparées.
- `nb_ent_total` : médiane de 49 ; 19 % des machines n'ont jamais été entretenues.
- Les distributions sont **fortement asymétriques**, d'où la visualisation en log(1 + x). Il faudra le prendre en compte : transformation log ou mise à l'échelle robuste pour le clustering.

**Redondances (corrélation de Spearman, |ρ| ≥ 0,9).** Le coefficient de Spearman est utilisé car il est robuste à l'asymétrie. Les paires les plus corrélées :
- `nb_rep_total` / `nb_arrets_distincts` (0,9997) ;
- `nb_rep_total` / `freq_rep_mensuelle` (0,98) ;
- `nb_rep_total` / `nb_natures_distinctes` (0,97) ;
- `nb_rep_total` / `duree_arret_totale` (0,96) ;
- `nb_ent_total` / `duree_ent_totale` (0,94).

La liste complète est exportée dans `paires_features_redondantes.csv`.

**Décision :** le dataset de référence conserve toutes les features. La **sélection finale se fera en Partie 2 / 3, selon la problématique** : K-means est sensible aux informations en double, alors qu'un modèle à base d'arbres l'est peu. Comme le dit le cahier des charges, *le Feature Engineering dépend de la question posée*.

---

## Étape 6 — Data Leakage

### 6.1 Variables à risque

| Variable | Risque | Traitement |
|---|---|---|
| `machine.cout_total / cout_reparation / cout_entretien` | cumuls ERP qui incluent les événements postérieurs à T | **supprimées** |
| `machine.etat` (« En panne », « Hors service ») | état à la date d'extraction : pour un T passé, révèle le futur, voire la cible | ajoutée **seulement si T ≥ extraction** |
| `machine.id_endroit` (emplacement courant) | instantané à l'extraction | remplacé par `type_endroit_T`, calculé depuis l'historique daté |
| `preventif.dernier / prochain_entretien_jour`, `avant_dernier` | instantané du planning à l'extraction | seule la fréquence est utilisée, et seulement si T ≥ extraction |
| entretiens futurs, `date_prevue` future | planification, non observée | lignes futures supprimées ; seul le retard des entretiens **passés** est utilisé |
| `duree_arret / duree_rep / date_cloture / date_fin_intervention` | connues **à la fin** de l'intervention | utilisées seulement comme historique (événements avant T). **Pour S3, elles constituent la cible et ne doivent jamais servir de features** |
| `cloture`, `a_probleme`, `changement` | renseignés pendant ou après l'intervention | même règle |
| lien appel → réparation | n'existe qu'après la prise en charge | pour S3, seuls la date d'appel et le problème déclaré sont disponibles au départ |

### 6.2 Test automatique

**Principe :** si les features à la date T n'utilisent que le passé, alors **supprimer tous les événements postérieurs à T ne doit rien changer** au résultat.

**Résultat :** à T = 2025-01-01, les deux tables de features sont **strictement identiques** (`assert_frame_equal`). Les colonnes instantanées sont bien absentes pour une date T passée. ✅

---

## Étape 7 — Synthèse

### 7.1 Comparaison avant / après

| Table | Lignes avant → après | Colonnes avant → après | Colonnes vides avant → après | % manquant avant → après |
|---|---|---|---|---|
| machine | 1 649 → 1 649 | 42 → 20 | 8 → 0 | 30,8 → 0,2 |
| reparation | 32 772 → 32 772 | 42 → 21 | 3 → 0 | 33,1 → 0,5 |
| appel | 32 331 → 32 331 | 14 → 8 | 4 → 0 | 28,8 → 0,7 |
| entretien | 65 173 → 63 899 | 18 → 12 | 2 → 0 | 23,2 → 1,2 |
| preventif | 4 109 → 4 109 | 16 → 9 | 5 → 0 | 47,8 → 7,7 |
| historique | 15 191 → 14 654 | 7 → 4 | 2 → 0 | 28,6 → 0,0 |

**Lecture**
- Le nettoyage **supprime peu de lignes** : doublons d'entretiens et de lectures d'emplacement, planifications futures.
- Il **supprime beaucoup de colonnes** : vides, constantes, redondantes ou source de fuite.
- Les valeurs manquantes résiduelles ont un sens métier : appel non consulté, entretien non planifié, machine sans préventif.

### 7.2 Datasets produits (`Partie1/outputs/`)

| Fichier | Lignes | Colonnes | Description |
|---|---:|---:|---|
| `reparations_enrichies.csv` | 32 772 | 39 | une ligne par réparation, décodée (nature, problème, ligne, machine, appel). **Base pour S3** |
| `machine_features_snapshot.csv` | 1 649 | 40 | une ligne par machine à T = 2026-03-06. **Base pour U1 / U2 / U3** |
| `machines_clean.csv` | 1 649 | 20 | référentiel des machines nettoyé, catégories regroupées |
| `entretiens_clean.csv` | 63 899 | 12 | entretiens observés (sans planification future ni doublons) |
| `appels_clean.csv` | 32 331 | 8 | appels de panne |
| `historique_emplacements_clean.csv` | 14 654 | 4 | lectures datées d'emplacement |
| `preventif_clean.csv` | 4 109 | 9 | configuration du préventif (machine × action) |
| `dictionnaire_features.csv` | — | — | documentation des features |
| `audit_qualite.csv` | 37 | — | problèmes de qualité chiffrés et décisions |
| `journal_transformations.csv` | 41 | — | traçabilité des transformations |
| `paires_features_redondantes.csv` | — | — | paires avec \|ρ\| ≥ 0,9 |

### 7.3 Limites connues des données

1. **Aucune documentation officielle de l'ERP.** Le sens de plusieurs champs reste une hypothèse (`changement`, `a_probleme`, `id_site*`, `PANNE NON ELIGIBLE`). L'unité en minutes est **démontrée** pour les réparations, mais seulement **supposée** pour `entretien.duree`, faute de date de fin.
2. **Indicateur de réalisation des entretiens inutilisable** (`faite = f` partout). Nous supposons qu'un entretien daté avant l'extraction a bien été réalisé.
3. **Historique court et hétérogène** : réparations depuis fin 2021, entretiens surtout depuis mi-2022. L'historique des machines anciennes est donc tronqué à gauche, ce que `exposition_jours` permet de compenser.
4. **Forte saisonnalité** (août) et **montée en charge de l'ERP** en début de période. En Partie 2, le découpage devra être chronologique, pas aléatoire.
5. **Parc déséquilibré** : 87 % de machines à coudre ; les autres catégories ont de faibles effectifs.
6. **`date_cloture` n'est pas la fin réelle de l'intervention** dans de nombreux cas (clôture administrative).
7. **Interventions multiples sur un même arrêt** (≈ 3 % des lignes) : additionner leurs durées surestime légèrement le temps d'arrêt cumulé.
8. **Qualité de saisie** : environ 15 % des lignes ne vérifient pas exactement *attente + réparation = arrêt*, et quelques dates d'achat sont postérieures aux premiers événements.
9. **Informations instantanées** (état, emplacement courant, préventif) : leur valeur passée ne peut pas être reconstruite.

### 7.4 Risques de Data Leakage (récapitulatif)
- Cumuls ERP (`cout_*`) : **supprimés**.
- États et configurations instantanés : **restreints à T ≥ extraction**.
- Planifications futures : **retirées** des tables d'événements.
- Variables connues seulement en fin d'intervention : **interdites comme features** pour S3.
- Toutes les agrégations sont **bornées à T**, ce que vérifie un **test automatique**.
- Pour la Partie 2 : **découpage chronologique** obligatoire, et méfiance envers toute performance anormalement élevée.

### 7.5 Conclusion

Les données reçues forment un **ERP relationnel dont l'intégrité référentielle est bonne, mais dont la qualité de contenu est inégale**. Après préparation, nous disposons :
- d'un **dataset événementiel** propre et décodé (`reparations_enrichies`) ;
- d'un **dataset machine × date T** avec environ 35 features documentées (`machine_features_snapshot`) ;
- d'une **fonction de construction des features sans fuite**, testée et prête pour les Parties 2 et 3.

---

# Partie 2 — Supervised Learning

⏳ **Pas encore commencée.**

Points prévus, issus de la Partie 1 :
- choisir une problématique : S1 (panne dans les N prochains jours), S2 (nombre de réparations futures) ou S3 (durée ou gravité d'une réparation) ;
- construire le dataset avec `build_machine_snapshot(T)` sur plusieurs dates T (S1/S2) ou avec `reparations_enrichies` (S3) ;
- construire la cible de façon **strictement postérieure à T** ;
- utiliser un découpage **chronologique**, une baseline et des métriques adaptées au déséquilibre des classes.

# Partie 3 — Unsupervised Learning

⏳ **Pas encore commencée.**
