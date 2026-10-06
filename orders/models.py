import uuid
from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    """注文ヘッダーモデル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="購入者")
    order_number = models.CharField(max_length=32, unique=True, verbose_name="注文番号")
    total_price = models.PositiveIntegerField(verbose_name="合計金額 (税込)")
    
    # 配送先情報
    shipping_name = models.CharField(max_length=100, verbose_name="お名前")
    shipping_postal_code = models.CharField(max_length=10, verbose_name="郵便番号")
    shipping_address = models.CharField(max_length=255, verbose_name="ご住所")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="注文日時")

    class Meta:
        verbose_name = "注文"
        verbose_name_plural = "注文一覧"
        ordering = ['-created_at']

    def __str__(self):
        return f"注文 #{self.order_number} ({self.user.username})"

    @classmethod
    def generate_order_number(cls):
        """一意な注文番号を生成 (例: ORD-8A3B1C2D)"""
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"


class OrderItem(models.Model):
    """注文明細モデル (購入時の価格・商品名をスナップショット保存)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="注文")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items', verbose_name="商品")
    product_name = models.CharField(max_length=200, verbose_name="購入時商品名")
    price = models.PositiveIntegerField(verbose_name="購入時単価 (税込)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="購入数量")

    class Meta:
        verbose_name = "注文明細"
        verbose_name_plural = "注文明細一覧"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def subtotal(self):
        """小計を計算"""
        return self.price * self.quantity
