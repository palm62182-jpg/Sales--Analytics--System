import os
import requests
import re
from collections import defaultdict

# ==========================================
# PART 0: DUMMY DATA SETUP (FOR RUNNING IMMEDIATELY)
# ==========================================
def create_sample_files():
    if not os.path.exists('data'): os.makedirs('data')
    # Creating a sample pipe-delimited file with some errors to test validation
    content = """TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region
T001|2024-12-01|P1|Laptop|2|45000|C001|North
T002|2024-12-02|P2|Mouse, Wireless|10|1,500|C002|South
B999|2024-12-03|P3|Broken Row|0|0|C003|East
T003|2024-12-04|P3|Monitor|1|15000|C004|West
T004|2024-12-05|P1|Laptop|1|45000|C001|North"""
    with open("sales_data.txt", "w", encoding="utf-8") as f:
        f.write(content)

# ==========================================
# PART 1: FILE I/O & PREPROCESSING
# ==========================================
def read_sales_data(filename):
    """Reads sales data handling different encodings."""
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(filename, 'r', encoding=enc) as file:
                lines = file.readlines()
                return [line.strip() for line in lines[1:] if line.strip()] # Skip header
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            return []
        except UnicodeDecodeError:
            continue
    return []

def parse_transactions(raw_lines):
    """Parses raw lines into clean dictionaries."""
    parsed = []
    for line in raw_lines:
        parts = line.split('|')
        if len(parts) != 8: continue # Skip incorrect field counts
        try:
            parsed.append({
                'TransactionID': parts[0],
                'Date': parts[1],
                'ProductID': parts[2],
                'ProductName': parts[3].replace(',', ''), # Handle commas in name
                'Quantity': int(parts[4].replace(',', '')), # Convert to int
                'UnitPrice': float(parts[5].replace(',', '')), # Convert to float
                'CustomerID': parts[6],
                'Region': parts[7]
            })
        except ValueError: continue
    return parsed

def validate_and_filter(transactions, region=None, min_amount=None):
    """Validates rules (IDs starting with T/P/C) and filters."""
    valid, invalid_count = [], 0
    for tx in transactions:
        # Validation Rules
        if (tx['Quantity'] > 0 and tx['UnitPrice'] > 0 and 
            tx['TransactionID'].startswith('T') and 
            tx['ProductID'].startswith('P') and 
            tx['CustomerID'].startswith('C')):
            valid.append(tx)
        else:
            invalid_count += 1
            
    filtered = [t for t in valid if (not region or t['Region'] == region) and 
                (not min_amount or (t['Quantity']*t['UnitPrice']) >= min_amount)]
    
    summary = {'total_input': len(transactions), 'invalid': invalid_count, 'final_count': len(filtered)}
    return filtered, invalid_count, summary

# ==========================================
# PART 2: DATA PROCESSING & ANALYSIS
# ==========================================
def calculate_total_revenue(transactions):
    """Sum of Qty * Price."""
    return sum(tx['Quantity'] * tx['UnitPrice'] for tx in transactions)

def region_wise_sales(transactions):
    """Stats per region sorted by sales."""
    total_rev = calculate_total_revenue(transactions)
    stats = defaultdict(lambda: {'total_sales': 0.0, 'transaction_count': 0})
    for tx in transactions:
        stats[tx['Region']]['total_sales'] += tx['Quantity'] * tx['UnitPrice']
        stats[tx['Region']]['transaction_count'] += 1
    for r in stats:
        stats[r]['percentage'] = round((stats[r]['total_sales'] / total_rev) * 100, 2)
    return dict(sorted(stats.items(), key=lambda x: x[1]['total_sales'], reverse=True))

def daily_sales_trend(transactions):
    """Groups stats by date."""
    trend = defaultdict(lambda: {'revenue': 0.0, 'transaction_count': 0, 'unique_customers': set()})
    for tx in transactions:
        d = tx['Date']
        trend[d]['revenue'] += tx['Quantity'] * tx['UnitPrice']
        trend[d]['transaction_count'] += 1
        trend[d]['unique_customers'].add(tx['CustomerID'])
    return {k: {**v, 'unique_customers': len(v['unique_customers'])} for k in sorted(trend.keys())}

# ==========================================
# PART 3: API INTEGRATION
# ==========================================
def fetch_all_products():
    """Fetches product data from DummyJSON API."""
    try:
        response = requests.get('https://dummyjson.com/products?limit=100')
        if response.status_code == 200:
            print("API Success: Products fetched.")
            return response.json().get('products', [])
    except Exception as e:
        print(f"API Failure: {e}")
    return []

def create_product_mapping(api_products):
    """Maps numeric ID to product info."""
    return {p['id']: {'category': p['category'], 'brand': p['brand'], 'rating': p['rating']} for p in api_products}

def enrich_sales_data(transactions, mapping):
    """Adds API data to transactions."""
    enriched = []
    for tx in transactions:
        # Extract numeric ID (e.g., 'P1' -> 1)
        try:
            num_id = int(re.search(r'\d+', tx['ProductID']).group())
            if num_id in mapping:
                tx.update({
                    'API_Category': mapping[num_id]['category'],
                    'API_Brand': mapping[num_id]['brand'],
                    'API_Rating': mapping[num_id]['rating'],
                    'API_Match': True
                })
            else:
                tx.update({'API_Category': None, 'API_Brand': None, 'API_Rating': None, 'API_Match': False})
        except:
            tx.update({'API_Match': False})
        enriched.append(tx)
    return enriched

def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """Saves final data back to pipe-delimited file."""
    if not enriched_transactions: return
    headers = list(enriched_transactions[0].keys())
    with open(filename, 'w') as f:
        f.write('|'.join(headers) + '\n')
        for tx in enriched_transactions:
            f.write('|'.join(str(tx[h]) for h in headers) + '\n')
    print(f"Saved enriched data to {filename}")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    create_sample_files()
    
    # 1. Load and Clean
    raw = read_sales_data("sales_data.txt")
    parsed = parse_transactions(raw)
    valid_data, inv_count, summary = validate_and_filter(parsed)
    
    # 2. Analyze
    print("\n--- Sales Analysis ---")
    print(f"Total Revenue: ${calculate_total_revenue(valid_data):,.2f}")
    print("Region Statistics:", region_wise_sales(valid_data))
    
    # 3. Enrich with API
    api_data = fetch_all_products()
    if api_data:
        mapping = create_product_mapping(api_data)
        enriched = enrich_sales_data(valid_data, mapping)
        save_enriched_data(enriched)
        print("\nProcess Complete. Check 'data/enriched_sales_data.txt' for results.")