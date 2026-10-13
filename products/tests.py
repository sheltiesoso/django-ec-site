from django.test import TestCase
from django.urls import reverse
from .models import Product


class ProductModelTest(TestCase):
    def setUp(self):
        self.in_stock_product = Product.objects.create(
            name="エチオピア イルガチェフェ",
            price=1500,
            stock=10,
            description="華やかなフローラルな香り。",
            is_active=True,
        )
        self.out_of_stock_product = Product.objects.create(
            name="ケニア AA",
            price=1800,
            stock=0,
            description="重厚なコクと明るい酸味。",
            is_active=True,
        )

    def test_str_representation(self):
        """__str__ が商品名を返すか検証"""
        self.assertEqual(str(self.in_stock_product), "エチオピア イルガチェフェ")

    def test_is_in_stock_property(self):
        """is_in_stock プロパティが在庫数に応じて正しくブール値を返すか検証"""
        self.assertTrue(self.in_stock_product.is_in_stock)
        self.assertFalse(self.out_of_stock_product.is_in_stock)


class ProductViewTest(TestCase):
    def setUp(self):
        self.active_product = Product.objects.create(
            name="コロンビア スプレモ",
            price=1200,
            stock=5,
            is_active=True,
        )
        self.inactive_product = Product.objects.create(
            name="非公開商品",
            price=9999,
            stock=10,
            is_active=False,
        )

    def test_product_list_view(self):
        """商品一覧ページで公開商品のみが表示され、非公開商品は表示されないか検証"""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "コロンビア スプレモ")
        self.assertNotContains(response, "非公開商品")

    def test_product_detail_view_active(self):
        """公開商品の詳細ページが200で取得できるか検証"""
        response = self.client.get(reverse('products:product_detail', args=[self.active_product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "コロンビア スプレモ")

    def test_product_detail_view_inactive_returns_404(self):
        """非公開商品の詳細ページは404を返すか検証"""
        response = self.client.get(reverse('products:product_detail', args=[self.inactive_product.pk]))
        self.assertEqual(response.status_code, 404)
