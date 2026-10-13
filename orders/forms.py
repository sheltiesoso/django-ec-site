import re
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
                'placeholder': '123-4567 または 1234567',
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

    def clean_shipping_name(self):
        name = self.cleaned_data.get('shipping_name', '').strip()
        if not name:
            raise forms.ValidationError("お名前を入力してください。")
        if len(name) < 2:
            raise forms.ValidationError("お名前は2文字以上で入力してください。")
        return name

    def clean_shipping_postal_code(self):
        postal_code = self.cleaned_data.get('shipping_postal_code', '').strip()
        if not postal_code:
            raise forms.ValidationError("郵便番号を入力してください。")
        
        # ハイフンなしの7桁数字なら 123-4567 形式に正規化
        if re.match(r'^\d{7}$', postal_code):
            return f"{postal_code[:3]}-{postal_code[3:]}"
        elif re.match(r'^\d{3}-\d{4}$', postal_code):
            return postal_code
        else:
            raise forms.ValidationError("郵便番号は「123-4567」または「1234567」の形式で入力してください。")

    def clean_shipping_address(self):
        address = self.cleaned_data.get('shipping_address', '').strip()
        if not address:
            raise forms.ValidationError("お届け先住所を入力してください。")
        if len(address) < 5:
            raise forms.ValidationError("お届け先住所を正しく詳細に入力してください（5文字以上）。")
        return address
