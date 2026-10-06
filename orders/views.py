from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .cart import Cart


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
