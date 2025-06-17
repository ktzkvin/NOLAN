from services.employee_data_access import load_hr_csv_from_blob
from utils.text_extraction import extract_person_name

async def handle(prompt: str) -> str:
    df = load_hr_csv_from_blob()
    
    name = extract_person_name(prompt)
    if not name:
        return "Nom de l'employé non détecté dans la requête."

    filtered = df[df["Name"].str.lower() == name.lower()]
    
    if filtered.empty:
        return f"Aucune donnée trouvée pour {name}."
    
    return filtered.to_string(index=False)
