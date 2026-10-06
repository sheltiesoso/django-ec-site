from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    """新規会員登録フォーム (標準Userを使用し、emailを必須項目として追加)"""
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="ご注文内容の確認等に使用します。"
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フォーム各要素にCSSスタイル用クラスを付与
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})
