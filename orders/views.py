from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from products.models import Product
from .cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem


def cart_detail(request):
    """カート内の一覧・小計・合計を表示するビュー"""
    cart = Cart(request)
    items = cart.get_items()
    total_price = cart.get_total_price()

    # 各商品の数量セレクト用リストを付与
    for item in items:
        max_q = min(item['product'].stock, 10)
        item['quantity_range'] = range(1, max_q + 1)

    return render(request, 'orders/cart_detail.html', {
        'cart_items': items,
        'total_price': total_price,
    })


@require_POST
def cart_add(request, product_id):
    """商品をカートに追加するビュー"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1
    except ValueError:
        quantity = 1

    if not product.is_in_stock:
        messages.error(request, f"申し訳ありません。「{product.name}」は売り切れです。")
        return redirect('products:product_detail', pk=product.pk)

    cart.add(product=product, quantity=quantity)
    messages.success(request, f"「{product.name}」をカートに追加しました。")
    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, product_id):
    """カート内の商品数量を更新するビュー"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart.remove(product)
            messages.info(request, f"「{product.name}」をカートから削除しました。")
        else:
            cart.update(product=product, quantity=quantity)
            messages.success(request, f"「{product.name}」の数量を更新しました。")
    except ValueError:
        messages.error(request, "不正な数量が指定されました。")

    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """商品をカートから削除するビュー"""
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.info(request, f"「{product.name}」をカートから削除しました。")
    return redirect('orders:cart_detail')


@login_required
def checkout(request):
    """注文確認および注文確定処理を行うビュー (transaction.atomic)"""
    cart = Cart(request)
    items = cart.get_items()
    total_price = cart.get_total_price()

    if not items:
        messages.warning(request, "カートに商品が入っていません。")
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. 在庫の再検証 (サーバー側検証)
                    for item in items:
                        product = Product.objects.get(id=item['product'].id)
                        if product.stock < item['quantity']:
                            raise ValueError(f"申し訳ありません。「{product.name}」の在庫が不足しています。(残り {product.stock} 点)")

                    # 2. Orderインスタンスの作成
                    order = form.save(commit=False)
                    order.user = request.user
                    order.order_number = Order.generate_order_number()
                    order.total_price = total_price
                    order.save()

                    # 3. OrderItemインスタンスの作成と在庫減算
                    for item in items:
                        product = Product.objects.get(id=item['product'].id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=product.price,
                            quantity=item['quantity']
                        )
                        # 在庫引き落とし
                        product.stock -= item['quantity']
                        product.save()

                    # 4. カートを完全にクリア
                    cart.clear()

                messages.success(request, f"ご注文が完了いたしました！(注文番号: {order.order_number})")
                return redirect('orders:order_complete', order_number=order.order_number)

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('orders:cart_detail')
    else:
        form = OrderCreateForm()

    return render(request, 'orders/checkout.html', {
        'cart_items': items,
        'total_price': total_price,
        'form': form,
    })


@login_required
def order_complete(request, order_number):
    """注文完了画面 (購入者本人のみアクセス可能)"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_complete.html', {
        'order': order,
    })
