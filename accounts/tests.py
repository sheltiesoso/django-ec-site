from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class SignUpViewTest(TestCase):
    def test_signup_page_status_code(self):
        """会員登録ページが200 OKで開くか検証"""
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "新規会員登録")

    def test_signup_success(self):
        """正しい入力で会員登録が成功し、自動ログインされてトップへリダイレクトされるか検証"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(reverse('accounts:signup'), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # DBにユーザーが存在することを確認
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')

        # ログイン状態になっていること（セッション確認）
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_missing_email(self):
        """メールアドレス未入力時にバリデーションエラーとなるか検証"""
        data = {
            'username': 'noemailuser',
            'email': '',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(reverse('accounts:signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('email' in response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='noemailuser').exists())

    def test_signup_password_mismatch(self):
        """パスワード不一致時に登録が拒否されるか検証"""
        data = {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass456!',
        }
        response = self.client.post(reverse('accounts:signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())


class AuthFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!',
        )

    def test_login_success(self):
        """正しい認証情報でログインできるか検証"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'TestPassword123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_failure(self):
        """誤ったパスワードでログインが失敗するか検証"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout(self):
        """POSTでのログアウトで認証セッションが破棄されるか検証"""
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
