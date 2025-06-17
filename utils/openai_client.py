import openai, os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_type = "azure"
openai.api_version = "2024-12-01-preview"
deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT")

INTENT_CATEGORIES = [
    "DocumentAnalysis",
    "PolicySearch",
    "EmployeeDataAccess",
    "DocumentGeneration",
    "AdminFunction",
    "UnknownIntent"
]

async def detect_intent(user_prompt):
    prompt = f"""
You are an HR assistant bot. Classify the following request into one of these general intent categories:

{INTENT_CATEGORIES}

Only return the intent name.

User request:
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
    intent = response['choices'][0]['message']['content'].strip()
    return intent
