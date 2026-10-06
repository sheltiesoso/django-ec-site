from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    """公開中の商品一覧を表示するビュー"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/product_list.html', {
        'products': products
    })


def product_detail(request, pk):
    """商品詳細を表示するビュー (非公開または存在しない場合は404)"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    # 数量選択用の選択肢リストを作成 (在庫数または最大10個まで)
    max_quantity = min(product.stock, 10)
    quantity_range = range(1, max_quantity + 1) if max_quantity > 0 else []

    return render(request, 'products/product_detail.html', {
        'product': product,
        'quantity_range': quantity_range,
    })
