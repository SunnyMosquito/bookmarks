from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.
class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='images_created')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField()  # 图片的源 URL
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True,
                               db_index=True)
    # 多对多关系，对图片点like的所有用户
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='images_liked',
                                       blank=True)
    total_likes = models.PositiveIntegerField(db_index=True,
                                              default=0)
    
    def get_absolute_url(self):
        return reverse('images:detail', args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            # slugify(value) If value is "Joel is a slug", 
            # the output will be "joel-is-a-slug".
            self.slug = slugify(self.title)
        super(Image,self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title
