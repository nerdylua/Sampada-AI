import requests
import time

BASE_URL = "http://127.0.0.1:8080"

# Track test results
results = {"success": [], "failure": [], "error": []}

def test_endpoint(method, endpoint, data=None, description=""):
    url = f"{BASE_URL}{endpoint}"
    print(f"Testing {description} ({method} {url})...")
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(f"✓ SUCCESS: {description}")
            content = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print(f"Response: {content}\n")
            results["success"].append(description)
            return response
        else:
            print(f"✗ FAILURE: {description} - Status Code: {response.status_code}")
            print(f"Response: {response.text}\n")
            results["failure"].append(f"{description} (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"✗ ERROR: {description} - {e}\n")
        results["error"].append(f"{description} ({e})")
        return None

def print_summary():
    total = len(results["success"]) + len(results["failure"]) + len(results["error"])
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"✓ Passed:    {len(results['success'])}")
    print(f"✗ Failed:    {len(results['failure'])}")
    print(f"⚠ Errors:    {len(results['error'])}")
    print("-" * 60)
    
    if results["success"]:
        print("\n✓ SUCCESSFUL TESTS:")
        for item in results["success"]:
            print(f"   • {item}")
    
    if results["failure"]:
        print("\n✗ FAILED TESTS:")
        for item in results["failure"]:
            print(f"   • {item}")
    
    if results["error"]:
        print("\n⚠ ERROR TESTS:")
        for item in results["error"]:
            print(f"   • {item}")
    
    print("\n" + "=" * 60)
    pass_rate = (len(results["success"]) / total * 100) if total > 0 else 0
    print(f"Pass Rate: {pass_rate:.1f}%")
    print("=" * 60)

def main():
    # Reset results
    results["success"].clear()
    results["failure"].clear()
    results["error"].clear()
    
    print("=" * 60)
    print("Testing Unified Screener API")
    print("=" * 60 + "\n")
    
    # Test root
    test_endpoint("GET", "/", description="Root endpoint")
    
    # Test login
    test_endpoint("POST", "/login", description="Login")
    
    # Test search
    search_response = test_endpoint("GET", "/search/Tata", description="Search Company")
    
    company_url = "company/tata-steel/500470/"
    if search_response and search_response.json():
        results_data = search_response.json()
        if results_data and isinstance(results_data, list) and len(results_data) > 0:
            company_url = results_data[0]['url']
            print(f"Using company URL: {company_url}\n")
    
    # Test screener endpoints
    test_endpoint("GET", f"/charts/{company_url}", description="Get Charts")
    test_endpoint("GET", f"/pe_charts/{company_url}", description="Get PE Charts")
    test_endpoint("GET", f"/peers/{company_url}", description="Get Peers")
    test_endpoint("GET", f"/quarterly_results/{company_url}", description="Get Quarterly Results")
    test_endpoint("GET", f"/profit_loss/{company_url}", description="Get Profit Loss")
    test_endpoint("GET", f"/announcements/{company_url}", description="Get Announcements")
    test_endpoint("GET", f"/concalls/{company_url}", description="Get Concalls")
    
    # Test custom query
    query_payload = {
        "query": "Market capitalization > 500 AND Price to earning < 15"
    }
    test_endpoint("POST", "/custom_query", data=query_payload, description="Custom Query")
    
    # Test query agent
    agent_payload = {
        "query": "Get me companies with PE ratio less than 15 and market cap greater than 500 crores"
    }
    test_endpoint("POST", "/query_agent", data=agent_payload, description="Query Agent")
    
    print_summary()

if __name__ == "__main__":
    print("Ensure the server is running on port 8080 before testing.\n")
    main()
