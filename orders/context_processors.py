from .cart import Cart


def cart_context(request):
    """全テンプレートで利用可能なカート情報のコンテキストプロセッサ"""
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_total_quantity': cart.get_total_quantity(),
    }
