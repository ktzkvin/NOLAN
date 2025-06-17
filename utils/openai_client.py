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
    "DocumentGeneration", "AdminFunction", "UnknownIntent"
]

async def detect_intent(user_prompt):
    prompt = f"""
You are an HR assistant bot. Classify this request into one of the categories: {INTENT_CATEGORIES}

Only return the intent name.

Request:
{user_prompt}
"""
    response = openai.ChatCompletion.create(
        engine=deployment_id,
        messages=[
            {"role": "system", "content": "You are an HR intent classifier."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response['choices'][0]['message']['content'].strip()