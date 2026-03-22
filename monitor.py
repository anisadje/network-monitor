import subprocess
from datetime import datetime
import os 
import time 

DEFAULT_INTERVAL = 10 # Intervalle de ping par défaut (secondes) si non spécifié dans hosts.conf

# Couleurs ANSI

VERT = "\033[32m"
ROUGE = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"
FOND_ROUGE = "\033[41m"

# CHARGEMENT DE LA CONFIGURATION

def load_hosts(filepath): 
    """
    Lit le fichier de configuration et retourne la liste des hôtes à surveiller
    """
    hotes = []
    try: 
        with open(filepath, "r") as f: 
            lignes = f.readlines()
            for ligne in lignes : 
                ligne = ligne.strip()

                # Ignorer les lignes vides et les commentaires
                if ligne == "" or ligne.startswith("#"): 
                    continue #on passe directement à la prochaine itération

                champs = ligne.split()
                if len(champs) < 2: 
                    print(f"Ligne ignorée (format invalide) : '{ligne}'")
                    continue
                hote = {"ip": champs[0], 
                        "nom": champs[1], 
                        "interval" : int(champs[2]) if len(champs)>=3 else DEFAULT_INTERVAL} #si il y a 3 éléments dans la liste
                hotes.append(hote)

    except FileNotFoundError:
        print(f"Erreur : fichier '{filepath}' introuvable.")
        return []
    
    return hotes 

# PING 

def ping_host(ip): 
    """
    Envoie un ping ICMP à l'adresse donnée et retourne son état de disponibilité

    Utilise la commande système ping :
        -c 1 : envoie un seul paquet (évite une boucle infinie)
        -W 1 : timeout de 1 seconde maximum

    Retourne True si l'hôte réponde (code de retour 0), False sinon.
    """
    #ping -c 1 - W 1 8.8.8.8 : -c 1 = envoie 1 paquet et s'arrête. 
    # -W 1 = attend max 1 seconde 

    resultat = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip], #la commande découpé 
        stdout=subprocess.DEVNULL, #on cache l'affichage du ping
        stderr=subprocess.DEVNULL
    )
    return resultat.returncode == 0 

# LOGGING

def log_event(ip, nom, status):
    """
    Enregistre un changement d'état dans le fichier log

    Le fichier est ouvert en mode 'append' pour ne jamer écraser l'historique
    """
    maintenant = datetime.now()
    maintenant = maintenant.strftime("%Y-%m-%d %H:%M:%S")
    with open("logs/monitor.log", "a") as f: 
        ligne = f"[{maintenant}] {ip} ({nom}) -> {status}\n"
        f.write(ligne)

# VERIFICATION D'UN HOTE

def check_hote(hote, etats_precedents):
    """
    Ping un hôte et détecte les changements d'état

    Si l'état a changé depuis le dernier ping (ex : UP puis DOWN),
    l'évènement est enregistré dans le log. 
    
    Une alerte visuelle est affichée si la machine est DOWN

    Retourne le statut actuelle (True = UP, False = DOWN)
    """
    ip = hote["ip"]
    nom = hote["nom"]
    nouveau_status = ping_host(ip)

    # Logger uniquement si l'état a changé (évite les doublons dans le log)
    if nouveau_status != etats_precedents.get(ip):
        etats_precedents[ip] = nouveau_status
        log_event(ip, nom, nouveau_status)

     # Alerte visuelle immédiate si la machine vient de tomber   
    if nouveau_status == False : 
        print(f"\n{FOND_ROUGE}{BOLD}⚠️  ALERTE : {nom} ({ip}) est DOWN ! {RESET}\n")

    return nouveau_status



# TABLEAU DE BORD

def afficher_dashboard(hosts, etats_precedents): 
    """
    Efface le terminal et affiche l'état actuel de toutes les machines.

    UP -> affiche 
    """
    os.system("clear")

    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{BOLD}=== SUPERVISION RESEAU - {maintenant} ==={RESET}")
    print("-" * 48)

    for hote in hosts: 
        ip = hote["ip"]
        nom = hote["nom"]
        status = etats_precedents.get(ip)

        if status == True: 
            etat = "UP"
            couleur = VERT
        elif status == False:
            etat = "DOWN"
            couleur = ROUGE
        else: 
            etat = "..."
            couleur = ""

        print(f"{nom.ljust(15)} {ip.ljust(18)} {couleur}{BOLD}{etat}{RESET}")


def afficher_rapport(hotes, total_pings, total_up):
    """
    Affiche le rapport de disponibilité final
    """
    largeur = os.get_terminal_size().columns
    print(f"\n{BOLD}{'RAPPORT DE DISPONIBILITE'.center(largeur)}{RESET}")
    print("-".center(largeur, "-"))
    for hote in hotes: 
        ip = hote["ip"]
        nom = hote["nom"]
        total = total_pings[ip]
        up = total_up[ip]
        pct = (up / total * 100) if total > 0 else 0

        ligne = f"{nom.ljust(15)} {ip.ljust(18)} {up}/{total} pings   {pct:.1f}% uptime"
        print(ligne.center(largeur))

def superviser(hotes):
    etats_precedents = {}
    total_pings = {}
    total_up = {}
    for hote in hotes: 
        etats_precedents[hote["ip"]] = None
        total_pings[hote["ip"]] = 0
        total_up[hote["ip"]] = 0
    try:
        while True : 
            for hote in hotes : 
                ip = hote["ip"]
                status = check_hote(hote, etats_precedents)
                total_pings[ip] += 1
                if status: 
                    total_up[ip] += 1
            afficher_dashboard(hotes, etats_precedents)
            time.sleep(5)
    except KeyboardInterrupt: 
        afficher_rapport(hotes, total_pings, total_up)

if __name__ == "__main__":
    hotes = load_hosts("config/hosts.conf")
    superviser(hotes)

    



