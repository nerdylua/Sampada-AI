from google import genai
from openai import OpenAI
import json
import requests
from credentials import google_api, openai_api, llm_provider
from schemas import Screener_Query
from scraper import login, run_custom_query

# Cache for available metrics (fetched once)
_cached_metrics = None

def fetch_available_metrics():
    """Fetch available metrics from screener.in API (one-time call)."""
    global _cached_metrics
    if _cached_metrics is not None:
        return _cached_metrics
    
    print("[METRICS] Fetching available metrics from screener.in...")
    all_metrics = {}
    
    # Search with common starting letters to get comprehensive list
    search_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y']
    
    for char in search_chars:
        try:
            response = requests.get(f"https://www.screener.in/api/ratio/search/?q={char}", timeout=5)
            if response.status_code == 200:
                for metric in response.json():
                    all_metrics[metric['name']] = metric.get('description', '')
        except:
            continue
    
    _cached_metrics = all_metrics
    print(f"[METRICS] Loaded {len(all_metrics)} available metrics")
    return all_metrics


def build_system_prompt(metrics: dict) -> str:
    """Build system prompt with available metrics."""
    metric_list = "\n".join([f"- {name}" for name in sorted(metrics.keys())])
    
    return f"""You are an expert at converting natural language queries into screener.in stock screening queries.

AVAILABLE METRICS (use these EXACT names):
{metric_list}

OPERATORS: >, <, >=, <=, =, AND, OR
NUMBERS: Use plain numbers (e.g., 500, 15, 1000)

QUERY FORMAT: <Metric> <operator> <value> [AND/OR <Metric> <operator> <value>]

EXAMPLES:
- "companies with PE less than 15" → "Price to Earning < 15"
- "high ROE low debt companies" → "Return on equity > 20 AND Debt to equity < 1"
- "large cap profitable companies" → "Market Capitalization > 10000 AND Profit after tax > 0"

IMPORTANT: 
- Use EXACT metric names from the list above
- Do NOT invent metric names
- Keep queries simple and valid"""


class ScreenerQueryService:
    def __init__(self, api_key: str = None, provider: str = None, driver_getter=None):
        self.provider = provider or llm_provider
        self._driver_getter = driver_getter
        
        # Fetch available metrics and build prompt
        self.metrics = fetch_available_metrics()
        self.system_prompt = build_system_prompt(self.metrics)
        
        if self.provider == "gemini":
            self.client = genai.Client(api_key=api_key or google_api)
        elif self.provider == "openai":
            self.openai_client = OpenAI(api_key=api_key or openai_api)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Use 'gemini' or 'openai'.")
    
    def _get_driver(self):
        """Get driver from persistent getter, or create new one if not set."""
        if self._driver_getter:
            return self._driver_getter()
        print("Warning: No persistent driver configured, creating new login session")
        return login()

    def generate_screener_query(self, user_query: str) -> Screener_Query:
        if self.provider == "gemini":
            return self._generate_with_gemini(user_query)
        elif self.provider == "openai":
            return self._generate_with_openai(user_query)
    
    def _generate_with_gemini(self, user_query: str) -> Screener_Query:
        print(f"[GEMINI] Generating query for: {user_query[:50]}...")
        full_prompt = f"{self.system_prompt}\n\nUser request: {user_query}"
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": Screener_Query,
            },
        )
        # Log token usage
        usage = getattr(response, 'usage_metadata', None)
        if usage is not None:
            print(f"[GEMINI TOKENS] Prompt: {getattr(usage, 'prompt_token_count', 'N/A')}, Response: {getattr(usage, 'candidates_token_count', 'N/A')}, Total: {getattr(usage, 'total_token_count', 'N/A')}")
        else:
            print("[GEMINI TOKENS] Usage data not available")
        print(f"[GEMINI] Response: {response.text}")
        result = Screener_Query.model_validate_json(response.text)
        return result
    
    def _generate_with_openai(self, user_query: str) -> Screener_Query:
        print(f"[OPENAI] Generating query for: {user_query[:50]}...")
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_query}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "screener_query",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "screener_query": {
                                "type": "string",
                                "description": "The screener.in query to execute"
                            }
                        },
                        "required": ["screener_query"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # Log token usage
        usage = response.usage
        if usage is not None:
            print(f"[OPENAI TOKENS] Prompt: {usage.prompt_tokens}, Response: {usage.completion_tokens}, Total: {usage.total_tokens}")
        else:
            print("[OPENAI TOKENS] Usage data not available")
        print(f"[OPENAI] Response: {response.choices[0].message.content}")
        result_json = json.loads(response.choices[0].message.content)
        result = Screener_Query.model_validate(result_json)
        return result

    def process_query(self, user_query: str) -> dict:
        try:
            print(f"[1] Processing query with provider: {self.provider}")
            screener_query_obj = self.generate_screener_query(user_query)
            print(f"[2] Generated: {screener_query_obj.screener_query}")
        except Exception as e:
            print(f"[ERROR] LLM failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
        
        try:
            print("[3] Getting driver...")
            driver = self._get_driver()
            print("[4] Executing query on screener.in...")
            output = run_custom_query(driver, screener_query_obj.screener_query)
            print("[5] Done")
        except Exception as e:
            print(f"[ERROR] Scraper failed: {e}")
            raise Exception(f"Scraper failed: {e}")
        
        return {
            "generated_query": screener_query_obj.screener_query,
            "results": output
        }
