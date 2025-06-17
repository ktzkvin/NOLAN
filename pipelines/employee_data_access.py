import os
import re
import openai
import pyodbc
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
deployment = os.getenv("AZURE_MODEL_DEPLOYMENT")
conn_str = os.getenv("AZURE_SQL_CONNECTION_STRING")

TABLE_SCHEMA = """
Table: employees

Colonnes :
- id (texte, ex: 'E001')
- nom (texte)
- email (texte)
- departement (texte)
- Manager (texte, 'Oui'/'Non')
- poste (texte)
- responsable (texte)
- date_embauche (texte, format: 'JJ/MM/AAAA')
- conges_droit_annuel (nombre)
- conges_utilises (nombre)
- conges_planifies (nombre)
- conges_restants (nombre)
- conges_maladie_droit (nombre)
- conges_maladie_utilises (nombre)
- conges_maladie_restants (nombre)
- remuneration_salaire (nombre)
- remuneration_eligible_prime (texte, 'VRAI'/'FAUX')
- remuneration_date_prochaine_evaluation (texte, 'JJ/MM/AAAA')
- avantages_regime_sante (texte)
"""

async def handle(prompt: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un assistant SQL. Ne réponds qu'avec une requête SQL valide pour SQL Server. "
                "N'ajoute aucun commentaire, explication ou balise markdown. La base contient une table `employees`."
                f"\n\n{TABLE_SCHEMA}"
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=messages,
            temperature=0,
        )
        raw_sql = response["choices"][0]["message"]["content"]
        sql_query = re.sub(r"```sql|```", "", raw_sql).strip()
    except Exception as e:
        return {
            "intent": "EmployeeDataAccess",
            "response": f"Erreur LLM: {e}"
        }

    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(sql_query, conn)
    except Exception as e:
        return {
            "intent": "EmployeeDataAccess",
            "response": f"Erreur SQL: {e}"
        }

    if df.empty:
        return {
            "intent": "EmployeeDataAccess",
            "response": "Aucun résultat trouvé pour cette requête."
        }

    rows = []
    for _, row in df.iterrows():
        lignes = [f"{col} : {row[col]}" for col in df.columns]
        rows.append("\n".join(lignes))

    response_text = "\n\n---\n\n".join(rows)

    return {
        "intent": "EmployeeDataAccess",
        "response": response_text
    }
