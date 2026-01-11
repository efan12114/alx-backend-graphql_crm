#!/usr/bin/env python3
"""
Order Reminders Script
Sends reminders for pending orders using GraphQL
"""

import os
import sys
import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')

import django
django.setup()

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json

def send_order_reminders():
    """
    Query GraphQL endpoint for pending orders and log reminders
    """
    # GraphQL endpoint
    graphql_url = "http://localhost:8000/graphql"
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    
    # GraphQL query to get pending orders from the last 7 days
    query = """
    query GetPendingOrders($fromDate: String!) {
        allOrders(orderDate_Gte: $fromDate) {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        email
                        name
                    }
                    totalAmount
                }
            }
        }
    }
    """
    
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url=graphql_url)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute query
        result = client.execute(
            gql(query),
            variable_values={"fromDate": seven_days_ago}
        )
        
        orders = result.get('allOrders', {}).get('edges', [])
        
        # Log orders to file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"\n[{timestamp}] Order Reminders Processed\n"
        log_message += "=" * 50 + "\n"
        
        if orders:
            for order_edge in orders:
                order = order_edge['node']
                order_id = order.get("id", "N/A")
                customer_email = order.get("customer", {}).get("email", "N/A")
                order_date = order.get("orderDate", "N/A")
                
                log_message += f"Order ID: {order_id}\n"
                log_message += f"Customer Email: {customer_email}\n"
                log_message += f"Order Date: {order_date}\n"
                log_message += "-" * 30 + "\n"
        else:
            log_message += "No orders found from the last 7 days\n"
        
        # Write to log file
        with open("/tmp/order_reminders_log.txt", "a") as f:
            f.write(log_message)
        
        print("Order reminders processed!")
        
    except Exception as e:
        error_msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {str(e)}\n"
        with open("/tmp/order_reminders_log.txt", "a") as f:
            f.write(error_msg)
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_order_reminders()