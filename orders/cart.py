from products.models import Product


class Cart:
    """セッションを利用したショッピングカート管理クラス"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """商品をカートに追加、または数量を変更"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        # 在庫数以上の注文を抑止
        if self.cart[product_id]['quantity'] > product.stock:
            self.cart[product_id]['quantity'] = product.stock

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product)
        else:
            self.save()

    def update(self, product, quantity):
        """数量の更新 (上書き)"""
        self.add(product, quantity=quantity, override_quantity=True)

    def remove(self, product):
        """カートから商品を削除"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """カートを完全に空にする"""
        if 'cart' in self.session:
            del self.session['cart']
            self.save()

    def save(self):
        """セッションの変更を保存"""
        self.session.modified = True

    def get_items(self):
        """カート内の商品明細リストを取得 (Productオブジェクト、単価、小計を含む)"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        items = []

        for product in products:
            item_data = self.cart[str(product.id)]
            quantity = item_data['quantity']
            total_price = product.price * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price,
                'total_price': total_price,
            })
        return items

    def get_total_price(self):
        """カート内の合計金額 (税込) を計算"""
        return sum(item['total_price'] for item in self.get_items())

    def get_total_quantity(self):
        """カート内の総商品点数を計算"""
        return sum(item['quantity'] for item in self.cart.values())

    def __len__(self):
        return self.get_total_quantity()
