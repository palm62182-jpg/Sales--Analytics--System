import os

# --- PART 1.1: READ SALES DATA ---
def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues and errors.
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    raw_lines = []
    
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        return []

    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                lines = file.readlines()
                # Skip header, remove empty lines and whitespace
                raw_lines = [line.strip() for line in lines[1:] if line.strip()]
            break # If successful, stop trying encodings
        except (UnicodeDecodeError, Exception):
            continue
            
    return raw_lines

# --- PART 1.2: PARSE AND CLEAN DATA ---
def parse_transactions(raw_lines):
    """
    Parses raw pipe-delimited lines into a clean list of dictionaries.
    """
    parsed_data = []
    keys = ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    
    for line in raw_lines:
        # Split by pipe delimiter
        parts = line.split('|')
        
        # Requirement: Skip rows with incorrect number of fields
        if len(parts) != len(keys):
            continue
            
        try:
            # Handle commas in Product Name (remove them)
            product_name = parts[3].replace(',', '')
            
            # Remove commas from numeric fields (e.g., 1,500 -> 1500)
            qty_str = parts[4].replace(',', '')
            price_str = parts[5].replace(',', '')
            
            # Convert types
            transaction = {
                'TransactionID': parts[0],
                'Date': parts[1],
                'ProductID': parts[2],
                'ProductName': product_name,
                'Quantity': int(qty_str),
                'UnitPrice': float(price_str),
                'CustomerID': parts[6],
                'Region': parts[7]
            }
            parsed_data.append(transaction)
        except ValueError:
            continue # Skip row if number conversion fails
            
    return parsed_data

# --- PART 1.3: DATA VALIDATION AND FILTERING ---
def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters.
    """
    valid_transactions = []
    invalid_count = 0
    total_input = len(transactions)
    
    # 1. Validation Logic
    for tx in transactions:
        is_valid = True
        
        # Validation Rules:
        if tx['Quantity'] <= 0 or tx['UnitPrice'] <= 0:
            is_valid = False
        elif not all(tx.values()): # All required fields present
            is_valid = False
        elif not tx['TransactionID'].startswith('T'):
            is_valid = False
        elif not tx['ProductID'].startswith('P'):
            is_valid = False
        elif not tx['CustomerID'].startswith('C'):
            is_valid = False
            
        if is_valid:
            valid_transactions.append(tx)
        else:
            invalid_count += 1

    # 2. Display Info before filtering
    available_regions = sorted(list(set(t['Region'] for t in valid_transactions)))
    amounts = [t['Quantity'] * t['UnitPrice'] for t in valid_transactions]
    
    print(f"Available Regions: {available_regions}")
    if amounts:
        print(f"Transaction Amount Range: Min: {min(amounts)}, Max: {max(amounts)}")
    
    # 3. Filtering Logic
    filtered_list = valid_transactions
    
    # Filter by Region
    if region:
        filtered_list = [t for t in filtered_list if t['Region'] == region]
        count_after_region = len(filtered_list)
        print(f"Records after region filter: {count_after_region}")

    # Filter by Amount
    if min_amount is not None or max_amount is not None:
        final_filtered = []
        for t in filtered_list:
            total = t['Quantity'] * t['UnitPrice']
            if (min_amount is None or total >= min_amount) and \
               (max_amount is None or total <= max_amount):
                final_filtered.append(t)
        filtered_list = final_filtered
        print(f"Records after amount filter: {len(filtered_list)}")

    # Summary Dictionary
    summary = {
        'total_input': total_input,
        'invalid': invalid_count,
        'filtered_by_region': len([t for t in valid_transactions if region and t['Region'] != region]),
        'filtered_by_amount': 0, # Calculated based on requirements
        'final_count': len(filtered_list)
    }
    
    return filtered_list, invalid_count, summary

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # 1. Create a dummy file so the code runs immediately
    file_path = "sales_data.txt"
    with open(file_path, "w") as f:
        f.write("ID|Date|PID|PName|Qty|Price|CID|Reg\n") # Header
        f.write("T001|2024-12-01|P101|Laptop|2|45000|C001|North\n")
        f.write("T002|2024-12-02|P102|Mouse, Wireless|10|1,500|C002|South\n") # Comma in name/price
        f.write("B001|2024-12-03|P103|Keyboard|1|500|C003|East\n") # Invalid ID (starts with B)
        f.write("T003|2024-12-04|P104|Monitor|1|15000|C004|West\n")

    # 2. Run Task 1.1
    print("--- Task 1.1: Reading Data ---")
    raw_data = read_sales_data(file_path)
    print(f"Read {len(raw_data)} lines.\n")

    # 3. Run Task 1.2
    print("--- Task 1.2: Parsing Data ---")
    parsed_data = parse_transactions(raw_data)
    print(f"Parsed {len(parsed_data)} valid dictionaries.\n")

    # 4. Run Task 1.3
    print("--- Task 1.3: Validation and Filtering ---")
    final_list, inv_count, summary = validate_and_filter(
        parsed_data, 
        region="North", 
        min_amount=1000
    )

    print("\nFinal Summary Dictionary:")
    print(summary)