from django import forms

from config.models import BWebtype
from backend_admin.models import User, GroupConfigEach


class ConfigEachForm(forms.Form):
    groups_name = forms.CharField(label='组名', max_length=30)
    users = forms.ModelMultipleChoiceField(label='选择配置人员', required=False,
                                           queryset=User.objects.filter(groups__name__contains='配置'),
                                           widget=forms.CheckboxSelectMultiple()
                                           )


class ConfigGroupForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(label='配置组', required=False,
                                            queryset=GroupConfigEach.objects.filter(),
                                            widget=forms.CheckboxSelectMultiple()
                                            )


class ConfigForm(forms.Form):
    webname = forms.CharField(label='网站名称', max_length=30, required=True)
    url = forms.CharField(label='网站域名', max_length=200, required=True)
    tag = forms.CharField(label='标签', max_length=200, required=True)
    tag1 = forms.CharField(label='标签1', max_length=200, required=True)
    tag2 = forms.CharField(label='标签2', max_length=200, required=True)
    tag3 = forms.CharField(label='标签3', max_length=200, required=True)
    webtype = forms.ModelChoiceField(label='网站类型', widget=forms.Select(), queryset=BWebtype.objects.all())
