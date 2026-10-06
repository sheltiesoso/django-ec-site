from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """注文時のお届け先情報入力フォーム"""

    class Meta:
        model = Order
        fields = ['shipping_name', 'shipping_postal_code', 'shipping_address']
        widgets = {
            'shipping_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '山田 太郎',
            }),
            'shipping_postal_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '123-4567',
            }),
            'shipping_address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '東京都渋谷区道玄坂1-2-3 ○○マンション101',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shipping_name'].label = "お名前"
        self.fields['shipping_postal_code'].label = "郵便番号"
        self.fields['shipping_address'].label = "お届け先住所"
