from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField("название группы", max_length=200)
    slug = models.SlugField("слэг", unique=True)
    description = models.TextField("описание группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("ваш пост", help_text="напишите свой пост здесь")
    pub_date = models.DateTimeField("дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="автор поста",
                               help_text="информация об авторе данного поста")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="posts", blank=True, null=True,
                              verbose_name="группа поста",
                              help_text="выберите группу из списка")
    #image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-pub_date']

    def __str__(self):
        return f"{self.text[:15], self.pub_date, self.author, self.group}"
