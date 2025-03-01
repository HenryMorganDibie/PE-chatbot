import openai
import os
from dotenv import load_dotenv
import pandas as pd
from google.oauth2.service_account import Credentials

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

KNOWN_RELATIONSHIPS = {
    "flourish ventures": "Madica is an Africa-focused pre-seed investment program launched in 2022 and affiliated with Flourish Ventures, a global venture capital firm. While Madica operates as a separate entity with its own governance, it benefits from Flourish Ventures' support and resources.",
}

SERVICE_ACCOUNT_FILE = "/Users/toyosioluwasijuwomi/Downloads/strong-province-451622-c7-5d87a51b9e96.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Example: Using pandas to read in Excel files
#steers_classification = pd.read_excel('/Users/toyosioluwasijuwomi/Downloads/Stears classification for Prompts .xlsx')
#countries_regions = pd.read_excel('/Users/toyosioluwasijuwomi/Downloads/Countries - regions for Prompts .xlsx')

def categorize_query(query):
    categories = {
        "transaction": ["acquisition", "deal", "buyout", "investment", "merger", "private placement", "fundraising"],
        "fund": ["IRR", "MOIC", "holding period", "sovereign wealth fund", "DFI", "pension fund", "fund formation"],
        "valuation": ["DCF", "multiples", "EBITDA", "NAV", "book value", "valuation in Africa", "pricing"],
        "exit": ["IPO", "secondary sale", "trade sale", "NSE", "JSE", "BRVM", "EGX", "exit challenges in Africa"],
        "lp_gp_dynamics": ["limited partner", "general partner", "carried interest", "fund structure", "capital calls"],
        "company_analysis": ["financial health", "due diligence", "credit risk", "FX risk", "African SMEs", "market sizing"],
        "regulatory": ["SEC Nigeria", "CMA Kenya", "FSCA South Africa", "PE regulations in Africa", "taxation", "local content rules"]
    }
    for category, keywords in categories.items():
        if any(word in query.lower() for word in keywords):
            return category
    return "general"

SYSTEM_MESSAGE = """
You are an expert AI assistant specializing in African Private Equity (PE) and related financial topics. Your responses should:
- Focus exclusively on Africa, using real-world examples from African PE transactions, DFIs, and sector trends.
- Provide data-driven insights based on the most current reports, trends, and news in African PE.
- Mention key African investors such as DFIs, Pension Funds, Sovereign Wealth Funds, Family Offices, and Private Equity firms.
- Discuss PE deal-making in major African regions (West Africa, East Africa, Southern Africa, North Africa, Central Africa).
- Ensure responses reflect the most up-to-date information, incorporating sector-specific trends, financial data, and insights into the African market.
- Provide specific details when asked about key African sectors like fintech, agribusiness, healthcare, energy, and technology.
- Highlight sectors that are producing the largest multiples on investments, including historical trends over the past 5 years.
- When asked about the dynamics between Limited Partners (LPs) and General Partners (GPs), explain how LPs provide capital and how GPs manage the fund, with specific focus on the African context and typical fund structures.
- Provide insights on the largest DFIs involved in direct investments in Africa and their activity in sectors like renewable energy, infrastructure, and agriculture.
- When asked for data or information about African private equity transactions, mention authoritative sources such as AVCA (African Private Equity and Venture Capital Association), Preqin, EMPEA, and other reputable platforms.
- Ensure all information provided is accurate and cite sources where applicable, including government business registries, official websites, and reputable industry reports.
- When asked for company profiles, provide key information such as legal name, year founded, industry, key executives, headquarters, ownership structure, and financial data where available.
- Provide concise biographies for management teams, including educational background, previous roles, and career highlights.
- If the user is asking for financial data extraction from an Annual Statement PDF, please capture relevant financial fields as outlined below:
  - Extract financial data for **Income Statement**, **Balance Sheet**, **Cash Flow Statement**, and additional fields like **EBITDA margin**, **Return on Equity**, and **Return on Assets**.
  - Abbreviated numbers should be scaled accordingly (e.g., 'K' for thousands, 'M' for millions).
  - Return a valid JSON format, replacing any missing or unknown values with `null`.
  - Ensure the metadata is included, like `reported_currency`, which should be the ISO currency code.
"""

def generate_prompt(query):
    for firm in KNOWN_RELATIONSHIPS:
        if firm in query.lower():
            return KNOWN_RELATIONSHIPS[firm]
    
    category = categorize_query(query)
    prompts = {
        "transaction": "Explain the steps in a typical private equity transaction in Africa.",
        "fund": "Describe key metrics used in African private equity fund performance and how DFIs influence fundraising.",
        "valuation": "How do PE firms value African companies, considering data limitations and currency risks?",
        "exit": "What are the most viable exit strategies for PE firms in Africa, and what challenges do they face?",
        "lp_gp_dynamics": "Explain the dynamics between LPs and GPs in African private equity, including capital constraints.",
        "company_analysis": "How do African PE firms assess a target company's financial health, given economic volatility?",
        "regulatory": "What are key regulatory considerations for private equity in Africa, including SEC Nigeria and CMA Kenya?",
        "company_profiles": "Provide the company's full legal name exactly as it appears on official documents. Constraint: Include suffixes (e.g., Inc., Ltd., Plc) as presented; do not alter them. Source: Official company website, legal documents, government business registries, or/and any other reputable as mentioned in the system message.",
        "management_bio": "Provide a concise biography of key management team members, including educational background and previous roles.",
        "financial_data_extraction": "Create prompts for extracting key financial data from PDFs such as revenue, net income, EBITDA, total assets, and debt.",
        "pe_queries": "Develop custom prompts for improving responses related to Private Equity queries including transaction steps, fund metrics, valuation methods, exit strategies, and LP/GP dynamics.",
        "article_summarization": "Create optimized prompts to summarize articles and extract election-related insights, including candidates, polling trends, election results, and controversies.",
        "macro_transaction_data": "Create structured prompts for extracting macroeconomic and transaction data in a tabular format for analytical purposes."
    }
    return prompts.get(category, f"Provide an African market-focused answer for: {query}")

def ask_openai(query):
    try:
        for firm in KNOWN_RELATIONSHIPS:
            if firm in query.lower():
                return KNOWN_RELATIONSHIPS[firm]
        
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": generate_prompt(query)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def log_response(query, old_response, new_response):
    with open("pe_chatbot_responses.txt", "a") as file:
        file.write(f"Query: {query}\nOld Response: {old_response}\nNew Response: {new_response}\n---\n")

def validate_response(response):
    authoritative_sources = {
        "IRR": "Internal Rate of Return (IRR) is a key metric in African PE, often affected by FX volatility and political risks.",
        "MOIC": "Multiple on Invested Capital (MOIC) is crucial for African PE, considering exit challenges and long investment horizons.",
        "Exit Strategies": "In Africa, IPOs are rare, with secondary sales and trade sales to multinationals and DFIs being more common.",
        "Regulations": "African PE is regulated by SEC Nigeria, CMA Kenya, FSCA South Africa, and OHADA (Francophone Africa's business law framework)."
    }
    for term, definition in authoritative_sources.items():
        if term.lower() in response.lower():
            response += f"\n\n[Validated: {definition}]"
    return response

if __name__ == "__main__":
    user_query = "How do DFIs in Africa assess the risk of a new fund formation?"
    old_response = ask_openai(user_query)
    new_response = validate_response(old_response)
    print("Response:", new_response)
    log_response(user_query, old_response, new_response)
