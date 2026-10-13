"""
Génère un faux fichier de transactions mobile money : transactions.csv

Les données sont FICTIVES. Elles contiennent des défauts volontaires
(doublons, montants vides ou négatifs, deux formats de date, villes mal écrites)
pour s'entraîner au nettoyage, comme dans le projet TARDIS.

Usage : python3 generate_data.py
"""

import csv
import random
from datetime import datetime, timedelta

# Même graine = même fichier à chaque lancement
random.seed(42)

NB_TRANSACTIONS = 5000
NB_DOUBLONS = 100
FICHIER_SORTIE = "transactions.csv"

TYPES = ["envoi", "retrait", "paiement_facture", "achat_credit"]
POIDS_TYPES = [35, 25, 15, 25]

VILLES = ["Cotonou", "Abomey-Calavi", "Porto-Novo", "Parakou",
          "Bohicon", "Ouidah", "Natitingou"]
POIDS_VILLES = [40, 15, 15, 12, 7, 6, 5]

# Poids de chaque heure de 0h à 23h : peu de transactions la nuit,
# des pics le matin (7h-9h) et le soir (18h-20h)
POIDS_HEURES = [1, 1, 1, 1, 1, 2, 4, 8, 10, 9, 7, 7,
                8, 7, 6, 6, 7, 8, 10, 10, 9, 6, 3, 2]


def choisir_date():
    debut = datetime(2026, 7, 1)
    jour = random.randint(0, 61)  # du 1er juillet au 31 août
    heure = random.choices(range(24), weights=POIDS_HEURES)[0]
    minute = random.randint(0, 59)
    seconde = random.randint(0, 59)
    return debut + timedelta(days=jour, hours=heure, minutes=minute, seconds=seconde)


def choisir_montant(type_operation):
    if type_operation == "achat_credit":
        return random.choice([100, 200, 500, 1000, 2000, 5000])
    if type_operation == "envoi":
        return random.randint(10, 2000) * 50       # de 500 à 100 000 FCFA
    if type_operation == "retrait":
        return random.randint(10, 2000) * 100      # de 1 000 à 200 000 FCFA
    return random.randint(20, 500) * 100           # facture : 2 000 à 50 000 FCFA


def choisir_statut(type_operation, heure):
    # Motif caché : les factures échouent plus souvent entre 19h et 21h
    if type_operation == "paiement_facture" and 19 <= heure < 21:
        risque = 0.14
    else:
        risque = 0.03
    if random.random() < risque:
        return "échoué"
    return "réussi"


def abimer_date(date):
    # 15 % des dates sont écrites au format jj/mm/aaaa au lieu de aaaa-mm-jj
    if random.random() < 0.15:
        return date.strftime("%d/%m/%Y %H:%M:%S")
    return date.strftime("%Y-%m-%d %H:%M:%S")


def abimer_montant(montant):
    tirage = random.random()
    if tirage < 0.015:
        return ""            # montant vide
    if tirage < 0.025:
        return -montant      # montant négatif (erreur de signe)
    return montant


def abimer_ville(ville):
    tirage = random.random()
    if tirage < 0.05:
        return ville.upper()           # "COTONOU"
    if tirage < 0.10:
        return ville.lower()           # "cotonou"
    if tirage < 0.15:
        return " " + ville + " "       # " Cotonou "
    return ville


def creer_transaction(numero):
    date = choisir_date()
    type_operation = random.choices(TYPES, weights=POIDS_TYPES)[0]
    ville = random.choices(VILLES, weights=POIDS_VILLES)[0]
    montant = choisir_montant(type_operation)
    statut = choisir_statut(type_operation, date.hour)
    return {
        "transaction_id": "TX" + str(numero).zfill(6),
        "date_heure": date,
        "type_operation": type_operation,
        "montant": montant,
        "ville": ville,
        "statut": statut,
    }


def abimer_transaction(transaction):
    transaction["date_heure"] = abimer_date(transaction["date_heure"])
    transaction["montant"] = abimer_montant(transaction["montant"])
    transaction["ville"] = abimer_ville(transaction["ville"])
    return transaction


def ajouter_doublons(transactions, nombre):
    for i in range(nombre):
        copie = dict(random.choice(transactions))
        position = random.randint(0, len(transactions))
        transactions.insert(position, copie)
    return transactions


def ecrire_csv(transactions, nom_fichier):
    colonnes = ["transaction_id", "date_heure", "type_operation",
                "montant", "ville", "statut"]
    with open(nom_fichier, "w", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(transactions)


def main():
    transactions = []
    for numero in range(1, NB_TRANSACTIONS + 1):
        transactions.append(creer_transaction(numero))

    # On trie par date puis on renumérote, pour que les identifiants suivent l'ordre
    transactions.sort(key=lambda t: t["date_heure"])
    for numero, transaction in enumerate(transactions, start=1):
        transaction["transaction_id"] = "TX" + str(numero).zfill(6)

    for transaction in transactions:
        abimer_transaction(transaction)
    transactions = ajouter_doublons(transactions, NB_DOUBLONS)

    ecrire_csv(transactions, FICHIER_SORTIE)
    print(len(transactions), "lignes écrites dans", FICHIER_SORTIE)


if __name__ == "__main__":
    main()
