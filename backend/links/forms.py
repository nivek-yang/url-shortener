from django import forms

from .models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        # 選擇要在表單中顯示的欄位
        fields = ['original_url', 'slug', 'password', 'notes', 'is_active']

        # (可選) 自訂欄位的標籤或小工具
        labels = {
            'original_url': '原始網址',
            'slug': '自訂短網址 (留空則自動產生)',
            'password': '密碼保護 (選填)',
            'notes': '備註說明',
            'is_active': '是否啟用',
        }
        widgets = {
            'password': forms.PasswordInput(
                render_value=True
            ),  # 讓密碼欄位在編輯時能顯示 (但不安全，建議留空讓使用者重設)
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 讓 slug 和 password 欄位不是必填的
        self.fields['slug'].required = False
        self.fields['password'].required = False
