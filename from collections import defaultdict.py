from collections import defaultdict

# --- Task 2.1: Sales Summary Calculator ---

def calculate_total_revenue(transactions):
    """Calculates total revenue from all transactions."""
    # Sum of (Quantity * UnitPrice) for all transactions
    return float(sum(tx['Quantity'] * tx['UnitPrice'] for tx in transactions))

def region_wise_sales(transactions):
    """Analyzes sales by region."""
    total_revenue = calculate_total_revenue(transactions)
    region_stats = {}
    
    # Calculate total sales and transaction counts per region
    for tx in transactions:
        reg = tx['Region']
        if reg not in region_stats:
            region_stats[reg] = {'total_sales': 0.0, 'transaction_count': 0}
        
        region_stats[reg]['total_sales'] += tx['Quantity'] * tx['UnitPrice']
        region_stats[reg]['transaction_count'] += 1
    
    # Calculate percentage and prepare final dictionary
    for reg in region_stats:
        sales = region_stats[reg]['total_sales']
        region_stats[reg]['percentage'] = round((sales / total_revenue) * 100, 2)
    
    # Sort by total_sales in descending order
    sorted_regions = dict(sorted(region_stats.items(), key=lambda x: x[1]['total_sales'], reverse=True))
    return sorted_regions

def top_selling_products(transactions, n=5):
    """Finds top n products by total quantity sold."""
    product_data = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    
    # Aggregate by ProductName
    for tx in transactions:
        name = tx['ProductName']
        product_data[name]['qty'] += tx['Quantity']
        product_data[name]['rev'] += tx['Quantity'] * tx['UnitPrice']
        
    # Sort by TotalQuantity descending
    sorted_products = sorted(
        [(name, data['qty'], data['rev']) for name, data in product_data.items()],
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_products[:n]

# --- Task 2.2: Date-based Analysis ---

def daily_sales_trend(transactions):
    """Analyzes sales trends by date."""
    daily_data = {}
    
    # Group by date and calculate metrics
    for tx in transactions:
        date = tx['Date']
        if date not in daily_data:
            daily_data[date] = {'revenue': 0.0, 'transaction_count': 0, 'customers': set()}
        
        daily_data[date]['revenue'] += tx['Quantity'] * tx['UnitPrice']
        daily_data[date]['transaction_count'] += 1
        daily_data[date]['customers'].add(tx['CustomerID'])
        
    # Format and sort chronologically
    trend = {}
    for date in sorted(daily_data.keys()):
        trend[date] = {
            'revenue': daily_data[date]['revenue'],
            'transaction_count': daily_data[date]['transaction_count'],
            'unique_customers': len(daily_data[date]['customers'])
        }
    return trend

def find_peak_sales_day(transactions):
    """Identifies the date with highest revenue."""
    trend = daily_sales_trend(transactions)
    if not trend:
        return None
    
    # Find max based on revenue
    peak_date = max(trend, key=lambda d: trend[d]['revenue'])
    return (peak_date, trend[peak_date]['revenue'], trend[peak_date]['transaction_count'])

# --- Task 2.3: Product Performance ---

def customer_analysis(transactions):
    """Analyzes customer purchase patterns."""
    cust_data = {}
    
    for tx in transactions:
        cid = tx['CustomerID']
        if cid not in cust_data:
            cust_data[cid] = {'total_spent': 0.0, 'purchase_count': 0, 'products': set()}
            
        cust_data[cid]['total_spent'] += tx['Quantity'] * tx['UnitPrice']
        cust_data[cid]['purchase_count'] += 1
        cust_data[cid]['products'].add(tx['ProductName'])
        
    # Final formatting and sorting by total_spent descending
    result = {}
    for cid in cust_data:
        result[cid] = {
            'total_spent': cust_data[cid]['total_spent'],
            'purchase_count': cust_data[cid]['purchase_count'],
            'avg_order_value': round(cust_data[cid]['total_spent'] / cust_data[cid]['purchase_count'], 2),
            'products_bought': sorted(list(cust_data[cid]['products']))
        }
        
    return dict(sorted(result.items(), key=lambda x: x[1]['total_spent'], reverse=True))

def low_performing_products(transactions, threshold=10):
    """Identifies products with low sales."""
    product_data = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    
    for tx in transactions:
        name = tx['ProductName']
        product_data[name]['qty'] += tx['Quantity']
        product_data[name]['rev'] += tx['Quantity'] * tx['UnitPrice']
        
    # Filter products with total quantity < threshold
    low_perf = [
        (name, data['qty'], data['rev']) 
        for name, data in product_data.items() 
        if data['qty'] < threshold
    ]
    
    # Sort by TotalQuantity ascending
    return sorted(low_perf, key=lambda x: x[1])

# --- Main Execution Block ---
if __name__ == "__main__":
    # Sample Data based on image examples
    sample_transactions = [
        {'Date': '2024-12-01', 'ProductName': 'Laptop', 'Quantity': 2, 'UnitPrice': 45000.0, 'CustomerID': 'C001', 'Region': 'North'},
        {'Date': '2024-12-01', 'ProductName': 'Mouse', 'Quantity': 5, 'UnitPrice': 500.0, 'CustomerID': 'C001', 'Region': 'North'},
        {'Date': '2024-12-02', 'ProductName': 'Webcam', 'Quantity': 4, 'UnitPrice': 3000.0, 'CustomerID': 'C002', 'Region': 'South'},
        {'Date': '2024-12-15', 'ProductName': 'Headphones', 'Quantity': 7, 'UnitPrice': 1500.0, 'CustomerID': 'C003', 'Region': 'North'},
        {'Date': '2024-12-15', 'ProductName': 'Laptop', 'Quantity': 1, 'UnitPrice': 45000.0, 'CustomerID': 'C004', 'Region': 'West'}
    ]

    print("--- 2.1 Total Revenue ---")
    print(f"Total: {calculate_total_revenue(sample_transactions)}")
    
    print("\n--- 2.1 Region-wise Sales ---")
    print(region_wise_sales(sample_transactions))
    
    print("\n--- 2.1 Top 3 Products ---")
    print(top_selling_products(sample_transactions, n=3))
    
    print("\n--- 2.2 Daily Trend ---")
    print(daily_sales_trend(sample_transactions))
    
    print("\n--- 2.2 Peak Sales Day ---")
    print(find_peak_sales_day(sample_transactions))
    
    print("\n--- 2.3 Customer Analysis ---")
    print(customer_analysis(sample_transactions))
    
    print("\n--- 2.3 Low Performing Products (Threshold 10) ---")
    print(low_performing_products(sample_transactions, threshold=10))