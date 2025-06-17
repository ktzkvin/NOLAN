import pandas as pd
from services.file_loader import load_blob_file
from io import BytesIO

async def handle(prompt: str) -> str:
    # Charger et parser correctement le CSV
    blob_data = load_blob_file("hr_dataset_fr_new.csv")
    try:
        df = pd.read_csv(BytesIO(blob_data), encoding="utf-8", sep=";", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(BytesIO(blob_data), encoding="latin1", sep=";", on_bad_lines="skip")


    # Extraction du nom depuis la question (simpliste)
    import re
    match = re.search(r"(?:de|d')\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", prompt)
    if not match:
        return "Je n'ai pas réussi à identifier la personne dans la question."

    nom_recherche = match.group(1).strip().lower()
    df["nom"] = df["nom"].str.lower()
    personne = df[df["nom"] == nom_recherche]

    if personne.empty:
        return f"Aucune donnée trouvée pour '{nom_recherche.title()}' dans la base RH."

    # Structurer la réponse
    ligne = personne.iloc[0]
    return f"""📄 **Fiche employé : {ligne['nom'].title()}**

- 📧 Email : {ligne['email']}
- 🏢 Département : {ligne['departement']}
- 👤 Poste : {ligne['poste']}
- 🗓️ Date d'embauche : {ligne['date_embauche']}

**Congés :**
- Droit annuel : {ligne['conges.droit_annuel']} jours
- Utilisés : {ligne['conges.utilises']} jours
- Planifiés : {ligne['conges.planifies']} jours
- Restants : {ligne['conges.restants']} jours

**Congés maladie :**
- Droit : {ligne['conges_maladie.droit']} jours
- Utilisés : {ligne['conges_maladie.utilises']} jours
- Restants : {ligne['conges_maladie.restants']} jours

**Rémunération :**
- Salaire : {ligne['remuneration.salaire']} €
- Prime éligible : {'Oui' if ligne['remuneration.eligible_prime'] else 'Non'}
- Prochaine évaluation : {ligne['remuneration.date_prochaine_evaluation']}

**Avantages :**
- Régime santé : {ligne['avantages.regime_sante']}
"""
