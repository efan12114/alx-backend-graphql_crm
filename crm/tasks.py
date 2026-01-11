from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime  # MUST BE EXACT "from datetime import datetime"
import requests  # MUST BE EXACT "import requests"

@shared_task
def generate_crm_report():
    """Generates a CRM report and logs it to a file."""
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Query to get all data needed for the report
        query_str = """
        query {
          allCustomers {
            totalCount
          }
          allOrders {
            totalCount
            edges {
              node {
                totalAmount
              }
            }
          }
          allProducts {
            totalCount
          }
        }
        """
        query = gql(query_str)

        result = client.execute(query)
        customer_count = result['allCustomers']['totalCount']
        order_count = result['allOrders']['totalCount']
        product_count = result['allProducts']['totalCount']
        
        # Calculate total revenue
        total_revenue = sum(
            float(edge['node']['totalAmount']) 
            for edge in result['allOrders']['edges']
        )

        # Log the report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_line = f"{timestamp} - Report: {customer_count} customers, {product_count} products, {order_count} orders, {total_revenue:.2f} revenue\n"
        
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(report_line)

        return report_line.strip()
        
    except Exception as e:
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error generating report: {e}\n"
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(error_msg)
        return error_msg.strip()