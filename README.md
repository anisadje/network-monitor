# Network Monitor

Un outil de supervision réseau en Python/Linux qui surveille la disponibilité de machines en temps réel.

> Projet réalisé dans le cadre d'un projet personnel pour mieux comprendre les cours de l'UE Réseaux
---

## Fonctionnalités

- **Ping automatique** de chaque machine via ICMP
- **Tableau de bord en temps réel** avec couleurs dans le terminal (UP en vert, DOWN en rouge)
- **Journal horodaté** des changements d'état dans un fichier log
- **Alertes visuelles** dans le terminal quand une machine tombe
- **Rapport de disponibilité** (% uptime par machine) à l'arrêt du programme

---

## Structure du projet

```
network-monitor/
├── config/
│   └── hosts.conf       # Liste des machines à surveiller
├── logs/
│   └── monitor.log      # Journal horodaté des événements
├── monitor.py           # Script principal
└── README.md
```

---

## Installation

Aucune dépendance externe — uniquement des modules Python standard.

```bash
git clone https://github.com/anisadje/network-monitor.git
cd network-monitor
mkdir -p logs
```

---

## Utilisation

### 1. Configurer les machines à surveiller

Édite le fichier `config/hosts.conf` :

```
# Format : IP_ou_hostname   nom_affiche   intervalle_secondes
192.168.1.1      Routeur          5
8.8.8.8          DNS-Google       10
github.com       GitHub           15
```

- Les lignes commençant par `#` sont ignorées
- L'intervalle est optionnel (défaut : 10 secondes)

### 2. Lancer la supervision

```bash
python3 monitor.py
```

### 3. Arrêter et afficher le rapport

```
Ctrl+C
```

Le rapport de disponibilité s'affiche automatiquement.

---

## Exemple de sortie

```
=== SUPERVISION RESEAU - 2026-03-21 18:22:03 ===
------------------------------------------------
Routeur         192.168.1.1        DOWN
DNS-Google      8.8.8.8            UP
GitHub          github.com         UP
```

```
=== RAPPORT DE DISPONIBILITÉ ===
------------------------------------------------
      Routeur         192.168.1.1        0/4 pings    0.0% uptime
      DNS-Google      8.8.8.8            4/4 pings  100.0% uptime
      GitHub          github.com         4/4 pings  100.0% uptime
```

---

## Format du fichier log

```
[2026-03-21 18:22:03] 192.168.1.1 (Routeur) -> False
[2026-03-21 18:22:03] 8.8.8.8 (DNS-Google) -> True
```

---

## Compatibilité

- **OS** : Linux / WSL
- **Python** : 3.6+
- **Dépendances** : aucune (modules standard uniquement : `subprocess`, `datetime`, `os`, `time`)

---

## Concepts mis en œuvre

- Protocole **ICMP** et supervision réseau par ping
- Parsing de fichier de configuration
- Gestion d'état et détection de changements
- Logging horodaté
- Affichage terminal avec codes **ANSI**
- Gestion des signaux (`KeyboardInterrupt`)