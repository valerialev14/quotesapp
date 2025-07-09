from django.db import models
from django.core.exceptions import ValidationError

class Source(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

class Quote(models.Model):
    text = models.TextField(unique=True)
    weight = models.PositiveIntegerField(default=1)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes')
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.source and self.source.quotes.count() >= 3 and self.pk is None:
            raise ValidationError(
                f"У источника '{self.source.name}' уже есть 3 цитаты. Нельзя добавить больше."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.text[:50]}... (Источник: {self.source.name})"

    class Meta:
        verbose_name = 'Цитата'
        verbose_name_plural = 'Цитаты'
