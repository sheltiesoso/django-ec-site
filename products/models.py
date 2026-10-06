from django.db import models


class Product(models.Model):
    """商品モデル"""
    name = models.CharField(max_length=200, verbose_name="商品名")
    description = models.TextField(verbose_name="商品説明")
    price = models.PositiveIntegerField(verbose_name="価格 (税込)")
    stock = models.PositiveIntegerField(default=0, verbose_name="在庫数")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="商品画像")
    is_active = models.BooleanField(default=True, verbose_name="公開フラグ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品一覧"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        """在庫があるかどうかを判定"""
        return self.stock > 0
