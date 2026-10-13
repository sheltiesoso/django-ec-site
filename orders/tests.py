from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product
from .models import Order, OrderItem
from .forms import OrderCreateForm


class CartSessionTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="ブラジル サントス",
            price=1000,
            stock=10,
            is_active=True,
        )

    def test_cart_add_and_detail(self):
        """商品をカートに追加し、カート詳細画面で金額と商品名が表示されるか検証"""
        response = self.client.post(
            reverse('orders:cart_add', args=[self.product.id]),
            {'quantity': 2},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ブラジル サントス")
        self.assertContains(response, "2000")  # 1000 * 2 = 2000

    def test_cart_update_quantity(self):
        """カート内の商品数量を変更できるか検証"""
        self.client.post(reverse('orders:cart_add', args=[self.product.id]), {'quantity': 1})
        response = self.client.post(
            reverse('orders:cart_update', args=[self.product.id]),
            {'quantity': 3},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "3000")

    def test_cart_remove(self):
        """カートから商品を削除できるか検証"""
        self.client.post(reverse('orders:cart_add', args=[self.product.id]), {'quantity': 1})
        response = self.client.post(
            reverse('orders:cart_remove', args=[self.product.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "カートに商品が入っていません")


class CheckoutTransactionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='Password123!',
        )
        self.product = Product.objects.create(
            name="グアテマラ アンティグア",
            price=1400,
            stock=5,
            is_active=True,
        )

    def test_checkout_requires_login(self):
        """未ログイン時のチェックアウトアクセスはログイン画面へリダイレクトされるか検証"""
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_checkout_successful_order_creation_and_stock_deduction(self):
        """注文確定時にOrder作成、在庫減算、価格スナップショット、カートクリアが正常に行われるか検証"""
        self.client.login(username='buyer', password='Password123!')

        # カートに2点追加
        self.client.post(reverse('orders:cart_add', args=[self.product.id]), {'quantity': 2})

        # 注文確定POST送信
        data = {
            'shipping_name': '購入 太郎',
            'shipping_postal_code': '100-0001',
            'shipping_address': '東京都千代田区千代田1-1',
        }
        response = self.client.post(reverse('orders:checkout'), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # 1. Orderの作成確認
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_price, 2800)
        self.assertEqual(order.shipping_name, '購入 太郎')

        # 2. OrderItemと単価スナップショットの確認
        item = OrderItem.objects.filter(order=order).first()
        self.assertIsNotNone(item)
        self.assertEqual(item.price, 1400)
        self.assertEqual(item.quantity, 2)

        # 3. 在庫が5点から3点に減算されているか確認
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # 4. カートが空になっているか確認
        cart_response = self.client.get(reverse('orders:cart_detail'))
        self.assertContains(cart_response, "カートに商品が入っていません")

    def test_checkout_rollback_when_stock_insufficient(self):
        """在庫不足時に注文がロールバックされ、Orderが作成されないか検証"""
        self.client.login(username='buyer', password='Password123!')

        # カートに3点追加
        self.client.post(reverse('orders:cart_add', args=[self.product.id]), {'quantity': 3})

        # 他のセッション等で在庫が1点に急減したと仮定
        self.product.stock = 1
        self.product.save()

        # 注文確定POST送信
        data = {
            'shipping_name': '購入 太郎',
            'shipping_postal_code': '100-0001',
            'shipping_address': '東京都千代田区千代田1-1',
        }
        response = self.client.post(reverse('orders:checkout'), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Orderがロールバックされて未作成であること
        self.assertFalse(Order.objects.filter(user=self.user).exists())
        self.assertContains(response, "在庫が不足しています")


class OrderAccessSecurityTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='user_a', password='Password123!')
        self.user_b = User.objects.create_user(username='user_b', password='Password123!')

        self.order_a = Order.objects.create(
            user=self.user_a,
            order_number=Order.generate_order_number(),
            shipping_name='ユーザーA',
            shipping_postal_code='100-0001',
            shipping_address='東京都港区1-1',
            total_price=3000,
        )

    def test_order_history_shows_only_own_orders(self):
        """注文履歴一覧にはログインユーザー本人の注文のみが表示されるか検証"""
        self.client.login(username='user_b', password='Password123!')
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.order_a.order_number)

    def test_order_detail_idor_protection(self):
        """【IDOR対策】他人の注文番号に直接アクセスした場合に 404 が返るか検証"""
        self.client.login(username='user_b', password='Password123!')
        response = self.client.get(reverse('orders:order_detail', args=[self.order_a.order_number]))
        self.assertEqual(response.status_code, 404)

        # 本人アクセス時は 200 が返るか確認
        self.client.login(username='user_a', password='Password123!')
        response_own = self.client.get(reverse('orders:order_detail', args=[self.order_a.order_number]))
        self.assertEqual(response_own.status_code, 200)
        self.assertContains(response_own, self.order_a.order_number)
