from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm


def signup(request):
    """新規会員登録ビュー"""
    if request.user.is_authenticated:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 登録直後にそのまま自動ログイン
            login(request, user)
            messages.success(request, f"{user.username} さん、会員登録が完了しました！")
            return redirect('products:product_list')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {
        'form': form
    })
