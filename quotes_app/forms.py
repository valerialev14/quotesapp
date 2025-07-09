from django import forms
from .models import Source, Quote

class QuoteForm(forms.ModelForm):
    source = forms.ModelChoiceField(
        queryset=Source.objects.all(),
        required=False,
        label="Выберите источник",
        empty_label="--- Выберите существующий источник ---"
    )
    new_source = forms.CharField(
        max_length=200,
        required=False,
        label="Или введите новый источник"
    )

    class Meta:
        model = Quote
        fields = ['text', 'weight', 'source', 'new_source']
        labels = {
            'text': 'Текст цитаты',
            'weight': 'Вес цитаты',
        }
        help_texts = {
            'weight': 'Чем выше вес, тем чаще цитата будет показываться (от 1 до 100).',
        }

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        new_source = cleaned_data.get('new_source')
        text = cleaned_data.get('text')

        if not source and not new_source:
            raise forms.ValidationError("Выберите существующий источник или введите новый.")
        if source and new_source:
            raise forms.ValidationError("Выберите только один вариант: либо существующий источник, либо новый.")

        # Если введён новый источник, создаётся объект Source
        if new_source:
            new_source = new_source.strip()
            if not new_source:
                raise forms.ValidationError("Новый источник не может быть пустым.")
            if Source.objects.filter(name__iexact=new_source).exists():
                raise forms.ValidationError(f"Источник '{new_source}' уже существует. Выберите его из списка.")
            source_obj = Source.objects.create(name=new_source)
            cleaned_data['source'] = source_obj
        else:
            if not source:
                raise forms.ValidationError("Необходимо выбрать существующий источник.")
            cleaned_data['source'] = source

        # Проверка на пустой текст цитаты
        if not text or text.strip() == '':
            raise forms.ValidationError("Текст цитаты не может быть пустым.")

        # Проверка на дубликаты текста
        if text and Quote.objects.filter(text__iexact=text).exists():
            raise forms.ValidationError("Цитата с таким текстом уже существует.")

        # Проверка на максимум 3 цитаты для источника
        if source and source.quotes.count() >= 3:
            raise forms.ValidationError(
                f"У источника '{source.name}' уже есть 3 цитаты. Нельзя добавить больше."
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.source = self.cleaned_data['source']
        if not instance.source:
            raise ValueError("Источник не установлен.")
        if commit:
            instance.save()
        return instance