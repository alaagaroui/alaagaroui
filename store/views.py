from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Category, CartItem, Order, OrderItem
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            # إنشاء طلب جديد
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                email=request.POST.get('email'),
                payment_method=request.POST.get('payment_method'),
                total_amount=product.price,
                status='pending'
            )
            
            # إنشاء عنصر الطلب
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
            
            # تحديث المخزون
            product.stock -= 1
            product.save()
            
            messages.success(request, 'تم تقديم طلبك بنجاح!')
            return redirect('store:order_success')
            
        except Exception as e:
            messages.error(request, 'حدث خطأ أثناء معالجة طلبك. الرجاء المحاولة مرة أخرى.')
            return redirect('store:checkout', product_id=product_id)
    
    return render(request, 'store/checkout.html', {
        'product': product
    })

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # التحقق من المخزون
    if product.stock <= 0:
        messages.error(request, 'عذراً، هذا المنتج غير متوفر حالياً')
        return redirect('store:product_detail', product_id=product_id)
    
    # التحقق مما إذا كان المنتج موجود بالفعل في السلة
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    # إذا كان المنتج موجود بالفعل، قم بزيادة الكمية
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'تم تحديث الكمية في السلة')
        else:
            messages.warning(request, 'عذراً، لا يمكن إضافة المزيد من هذا المنتج')
    else:
        messages.success(request, 'تمت إضافة المنتج إلى السلة')
    
    return redirect('store:cart')

@login_required
def cart_checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, 'سلة التسوق فارغة')
        return redirect('store:cart')
        
    total = sum(item.get_total() for item in cart_items)
    
    if request.method == 'POST':
        try:
            # إنشاء طلب جديد
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                email=request.POST.get('email'),
                payment_method=request.POST.get('payment_method'),
                total_amount=total
            )
            
            # إنشاء عناصر الطلب
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # تحديث المخزون
                item.product.stock -= item.quantity
                item.product.save()
            
            # حذف محتويات السلة
            cart_items.delete()
            
            messages.success(request, 'تم تقديم طلبك بنجاح!')
            return redirect('store:order_success')
            
        except Exception as e:
            messages.error(request, 'حدث خطأ أثناء معالجة طلبك. الرجاء المحاولة مرة أخرى.')
            return redirect('store:cart_checkout')
        
    return render(request, 'store/cart_checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def profile(request):
    # الحصول على طلبات المستخدم
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # الحصول على منتجات السلة
    cart_items = CartItem.objects.filter(user=request.user)
    
    # حساب إجمالي المشتريات
    total_spent = sum(order.total_amount for order in orders)
    
    # حساب عدد الطلبات
    orders_count = orders.count()
    
    context = {
        'orders': orders,
        'cart_items': cart_items,
        'total_spent': total_spent,
        'orders_count': orders_count,
        'user': request.user
    }
    
    return render(request, 'store/profile.html', context)

@login_required
def order_success(request):
    return render(request, 'store/order_success.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

@ensure_csrf_cookie
def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'تم تسجيل الخروج بنجاح')
        return redirect('store:home')
    return render(request, 'store/logout.html')

@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminLogoutView(View):
    template_name = 'admin/admin_logout.html'

    def get(self, request):
        if not request.user.is_staff:
            return redirect('admin:login')
        return render(request, self.template_name)

    def post(self, request):
        if not request.user.is_staff:
            return redirect('admin:login')
        logout(request)
        messages.success(request, 'تم تسجيل الخروج من لوحة الإدارة بنجاح')
        return redirect('admin:login')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'مرحباً {username}! تم تسجيل دخولك بنجاح.')
                # إذا كان المستخدم مشرفاً، قم بتوجيهه إلى لوحة الإدارة
                if user.is_staff:
                    return redirect('admin:index')
                # وإلا قم بتوجيهه إلى الصفحة الرئيسية
                return redirect('store:home')
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})