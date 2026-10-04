import csv
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import ProductForm, StaffCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

# 1. The New Main Dashboard (Blocks)
@login_required
def home(request):
    return render(request, 'inventory/home.html')

# 2. The Products Page
@login_required
def product_list(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    query = request.GET.get('q', '') 
    if query:
        products = Product.objects.select_related('supplier').filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        )
    else:
        products = Product.objects.select_related('supplier').all()

    return render(request, 'inventory/products.html', {
        'products': products, 
        'form': form,
        'search_query': query
    })

# 3. Delete Logic
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('product_list')
@login_required
def staff_list(request):
    # 1. Handle new staff creation
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_list')
    else:
        form = StaffCreationForm()

    # 2. Get all registered users
    staff_members = User.objects.all().order_by('-date_joined')
    
    return render(request, 'inventory/staff.html', {
        'form': form,
        'staff_members': staff_members
    })
@login_required
def delete_staff(request, pk):
    # Sirf admin hi staff ko delete kar sakta hai
    if request.user.is_superuser:
        staff_member = get_object_or_404(User, pk=pk)
        
        # Admin khud ko galti se delete na kar de, isliye ye check zaroori hai
        if request.user != staff_member:
            staff_member.delete()
            
    return redirect('staff_list')
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        # instance=product batata hai ki naya banaye nahi, balki purane ko update karein
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        # Form ko purane data ke saath load karein
        form = ProductForm(instance=product)
        
    return render(request, 'inventory/edit_product.html', {'form': form, 'product': product})
# Update imports at the top:
from .models import Product, Order
from .forms import ProductForm, StaffCreationForm, OrderForm

# Add this function at the bottom of the file:
@login_required
def order_list(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 1. Save the new order to the database
            order = form.save()
            
            # 2. AUTOMATION: If the order is 'Received', increase the product's stock
            if order.status == 'Received':
                product = order.product
                product.stock_quantity += order.quantity
                product.save()
                
            return redirect('order_list')
    else:
        form = OrderForm()

    orders = Order.objects.select_related('product').all().order_by('-order_date')
    
    return render(request, 'inventory/orders.html', {'form': form, 'orders': orders})
@login_required
def export_products_csv(request):
    # Set up the HTTP response to tell the browser this is a file download
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    
    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['SKU', 'Product Name', 'Supplier', 'Stock Level', 'Price'])
    
    # Fetch data and write rows
    products = Product.objects.select_related('supplier').all()
    for product in products:
        writer.writerow([
            product.sku, 
            product.name, 
            product.supplier.name if product.supplier else 'N/A', 
            product.stock_quantity, 
            product.price
        ])
        
    return response