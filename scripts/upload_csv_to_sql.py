import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv

load_dotenv()

conn_str = os.getenv("AZURE_SQL_CONNECTION_STRING")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Création table
cursor.execute("""
IF OBJECT_ID('employees', 'U') IS NULL
CREATE TABLE employees (
    id NVARCHAR(10),
    nom NVARCHAR(255),
    email NVARCHAR(255),
    departement NVARCHAR(255),
    Manager NVARCHAR(10),
    poste NVARCHAR(255),
    responsable NVARCHAR(10),
    date_embauche NVARCHAR(50),
    conges_droit_annuel FLOAT,
    conges_utilises FLOAT,
    conges_planifies FLOAT,
    conges_restants FLOAT,
    conges_maladie_droit FLOAT,
    conges_maladie_utilises FLOAT,
    conges_maladie_restants FLOAT,
    remuneration_salaire FLOAT,
    remuneration_eligible_prime NVARCHAR(10),
    remuneration_date_prochaine_evaluation NVARCHAR(50),
    avantages_regime_sante NVARCHAR(255)
)
""")
conn.commit()

# Lecture du CSV
df = pd.read_csv("assets/docs/hr_dataset_fr_new.csv", sep=";", encoding="latin1")

# Nettoyage des colonnes numériques
float_columns = [
    "conges.droit_annuel", "conges.utilises", "conges.planifies", "conges.restants",
    "conges_maladie.droit", "conges_maladie.utilises", "conges_maladie.restants",
    "remuneration.salaire"
]
for col in float_columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .replace("", None)
        .apply(pd.to_numeric, errors="coerce")
    )

# Remplissage de NaN en None pour SQL
df = df.where(pd.notnull(df), None)

# Insertion
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()

print("Toutes les données ont été insérées avec succès dans la base de données SQL Azure.")