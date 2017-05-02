from django import forms


class ChangePasswordForm(forms.Form):
    now_password = forms.CharField(label='当前密码', max_length=16, min_length=6,
                                   widget=forms.TextInput(attrs={"class": 'form-control'}))
    new_password = forms.CharField(label='新密码', max_length=16, min_length=6,
                                   widget=forms.TextInput(attrs={"class": 'form-control'}),
                                   help_text='密码在6到16位之间，必须包含字母和数字')
    new_password1 = forms.CharField(label='请再次输入密码1', max_length=16, min_length=6,
                                    widget=forms.TextInput(attrs={"class": 'form-control'}))

    def clean(self):
        password_2 = self.cleaned_data['new_password1']
        password_1 = self.cleaned_data['new_password']
        if password_1 and password_2 and password_2 != password_1:
            raise forms.ValidationError('您输入的密码不一致')
