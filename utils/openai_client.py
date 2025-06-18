import openai, os
from dotenv import load_dotenv
load_dotenv()

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

deployment_id = os.getenv("AZURE_MODEL_DEPLOYMENT")

INTENT_CATEGORIES = [
    "DocumentAnalysis", "PolicySearch", "EmployeeDataAccess",
    "DocumentGeneration", "AdminFunction", "Autre"
]

async def detect_intent(user_prompt):
    response = openai.ChatCompletion.create(
        engine=deployment_id,
        messages=[
            {
                "role": "system",
                "content": "Tu es un classificateur d'intention. Réponds uniquement par un des mots suivants, sans rien d'autre : DocumentAnalysis, PolicySearch, EmployeeDataAccess, DocumentGeneration, AdminFunction, Autre."
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0
    )
    return response['choices'][0]['message']['content'].strip()
