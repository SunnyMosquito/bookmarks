from django import forms
from .models import Image
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify

class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        # 隐藏url域
        widgets = {
            'url': forms.HiddenInput
        }

    # 表单执行is_valid()时会调用该函数，
    # 检查后缀是不是图片，不算就返回错误
    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png']
        extension = url.split('.')[-1].lower() # 取文件后缀
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not '
                                        'match valid image extensions.')
        return url
    
    # 重写save方法，将url的图片下载，
    # 存储到Image的image字段
    # force_insert = False, force_update = False,
    def save(self, commit=True):
        # 实例化Image，不提交保存
        image = super(ImageCreateForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        # 此处有bug，中文title会返回None值，
        # 在detail视图会出现参数错误，后续会将中文改成拼音
        image_name = '{}.{}'.format(slugify(image.title),
                                    image_url.split('.')[-1].lower())
        response = request.urlopen(image_url)
        # 保存image
        image.image.save(image_name,
                         ContentFile(response.read()),
                         save=False)
        
        if commit:
            image.save()
        
        return image
