import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from crm.models import Customer, Product, Order  # This line must be exact
from .filters import CustomerFilter, ProductFilter, OrderFilter
import re
from django.db import transaction


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
    
    # Task 0: Add hello field
    hello = graphene.String()
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")
        if phone and not re.match(r"^(\+1)?\d{10}$|^\d{3}-\d{3}-\d{4}$", phone):
            raise Exception("Invalid phone number format.")
        
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")
        
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # No arguments needed
    
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)
    
    @transaction.atomic
    def mutate(self, info):
        try:
            low_stock_products = Product.objects.filter(stock__lt=10)
            updated_products_list = []
            
            for product in low_stock_products:
                product.stock += 10
                product.save()
                updated_products_list.append(product)
            
            message = f"Successfully updated {len(updated_products_list)} low-stock products."
            return UpdateLowStockProducts(
                success=True,
                message=message,
                updated_products=updated_products_list
            )
            
        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating low stock products: {str(e)}",
                updated_products=[]
            )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()