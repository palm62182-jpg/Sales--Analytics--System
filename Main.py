import os
import sys
import subprocess
import datetime
import csv
import re
from collections import defaultdict

# --- AUTO-INSTALLER FOR THE 'REQUESTS' LIBRARY ---
try:
    import requests
except ImportError:
    print("Installing missing 'requests' library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# ==========================================
# PART 1: DATA PROCESSING FUNCTIONS
# ==========================================

def read_and_parse(filename):
    """Reads CSV/TXT, handles encoding, and cleans data."""
    data = []
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                # Detect delimiter (comma for .csv, pipe for .txt)
                dialect = csv.Sniffer().sniff(f.read(1024))
                f.seek(0)
                reader = csv.DictReader(f, dialect=dialect)
                for row in reader:
                    # Clean numeric values (remove commas, currency symbols)
                    qty_str = str(row['Quantity']).replace(',', '')
                    price_str = str(row['UnitPrice']).replace(',', '').replace('₹', '')
                    
                    data.append({
                        'TransactionID': row['TransactionID'].strip(),
                        'Date': row['Date'].strip(),
                        'ProductID': row['ProductID'].strip(),
                        'ProductName': row['ProductName'].strip().replace(',', ''),
                        'Quantity': int(float(qty_str)),
                        'UnitPrice': float(price_str),
                        'CustomerID': row['CustomerID'].strip(),
                        'Region': row['Region'].strip()
                    })
                return data
        except Exception:
            continue
    return []

def validate_transactions(transactions):
    """Applies strict validation rules."""
    valid, invalid_count = [], 0
    for tx in transactions:
        # Rule: Qty > 0, Price > 0, Correct ID starts
        if (tx['Quantity'] > 0 and tx['UnitPrice'] > 0 and 
            tx['TransactionID'].startswith('T') and 
            tx['ProductID'].startswith('P') and 
            tx['CustomerID'].startswith('C')):
            valid.append(tx)
        else:
            invalid_count += 1
    return valid, invalid_count

# ==========================================
# PART 2: ANALYSIS & API
# ==========================================

def perform_analysis(transactions):
    """Calculates all metrics for the report."""
    analysis = {
        'total_revenue': sum(t['Quantity'] * t['UnitPrice'] for t in transactions),
        'regions': defaultdict(lambda: {'sales': 0.0, 'count': 0}),
        'products': defaultdict(lambda: {'qty': 0, 'rev': 0.0}),
        'customers': defaultdict(lambda: {'spent': 0.0, 'count': 0}),
        'daily': defaultdict(lambda: {'rev': 0.0, 'tx': 0, 'cust': set()})
    }
    
    for t in transactions:
        amt = t['Quantity'] * t['UnitPrice']
        analysis['regions'][t['Region']]['sales'] += amt
        analysis['regions'][t['Region']]['count'] += 1
        analysis['products'][t['ProductName']]['qty'] += t['Quantity']
        analysis['products'][t['ProductName']]['rev'] += amt
        analysis['customers'][t['CustomerID']]['spent'] += amt
        analysis['customers'][t['CustomerID']]['count'] += 1
        analysis['daily'][t['Date']]['rev'] += amt
        analysis['daily'][t['Date']]['tx'] += 1
        analysis['daily'][t['Date']]['cust'].add(t['CustomerID'])
        
    return analysis

def fetch_api_products():
    """Fetches product enrichment data."""
    try:
        resp = requests.get('https://dummyjson.com/products?limit=100', timeout=5)
        return {p['id']: p for p in resp.json().get('products', [])}
    except:
        return {}

# ==========================================
# PART 3: MAIN WORKFLOW
# ==========================================

def main():
    try:
        print("="*40)
        print("         SALES ANALYTICS SYSTEM")
        print("="*40)

        # 1 & 2. Read and Parse
        print("\n[1/10] Reading sales data...")
        filename = 'cleaned_sales_data.csv'
        raw_data = read_and_parse(filename)
        print(f"✓ Successfully read {len(raw_data)} transactions")

        print("\n[2/10] Parsing and cleaning data...")
        # (Cleaning happened during read)
        print(f"✓ Parsed {len(raw_data)} records")

        # 4 & 5. Filtering
        regions = sorted(list(set(t['Region'] for t in raw_data)))
        amounts = [t['Quantity'] * t['UnitPrice'] for t in raw_data]
        
        print(f"\n[3/10] Filter Options Available:")
        print(f"Regions: {', '.join(regions)}")
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")
        
        do_filter = input("\nDo you want to filter data? (y/n): ").lower()
        working_data = raw_data
        if do_filter == 'y':
            reg_choice = input(f"Enter Region: ")
            working_data = [t for t in raw_data if t['Region'] == reg_choice]
            print(f"✓ Filtered to {len(working_data)} records.")

        # 6 & 7. Validation
        print("\n[4/10] Validating transactions...")
        valid_data, inv_count = validate_transactions(working_data)
        print(f"✓ Valid: {len(valid_data)} | Invalid: {inv_count}")

        # 8. Analysis
        print("\n[5/10] Analyzing sales data...")
        metrics = perform_analysis(valid_data)
        print("✓ Analysis complete")

        # 9. API Fetch
        print("\n[6/10] Fetching product data from API...")
        api_data = fetch_api_products()
        print(f"✓ Fetched {len(api_data)} products")

        # 10. Enrichment
        print("\n[7/10] Enriching sales data...")
        enriched_count = 0
        failed_prods = set()
        for t in valid_data:
            match = re.search(r'\d+', t['ProductID'])
            if match and int(match.group()) in api_data:
                t['API_Category'] = api_data[int(match.group())]['category']
                enriched_count += 1
            else:
                failed_prods.add(t['ProductName'])
        print(f"✓ Enriched {enriched_count}/{len(valid_data)} transactions ({(enriched_count/len(valid_data)*100):.1f}%)")

        # 11. Save Enriched
        print("\n[8/10] Saving enriched data...")
        os.makedirs('data', exist_ok=True)
        with open('data/enriched_sales_data.txt', 'w', encoding='utf-8') as f:
            f.write("|".join(valid_data[0].keys()) + "\n")
            for t in valid_data: f.write("|".join(str(v) for v in t.values()) + "\n")
        print("✓ Saved to: data/enriched_sales_data.txt")

        # 12. Report
        print("\n[9/10] Generating report...")
        os.makedirs('output', exist_ok=True)
        report_path = 'output/sales_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*45 + "\n    SALES ANALYTICS REPORT\n" + "="*45 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Revenue: ₹{metrics['total_revenue']:,.2f}\n")
            f.write("\nREGION PERFORMANCE:\n")
            for r, s in sorted(metrics['regions'].items(), key=lambda x: x[1]['sales'], reverse=True):
                f.write(f"{r:<10}: ₹{s['sales']:,.0f}\n")
        print(f"✓ Report saved to: {report_path}")

        print("\n[10/10] Process Complete!")
        print("="*40)

    except Exception as e:
        print(f"\n✘ ERROR: {e}")

if __name__ == "__main__":
    main()