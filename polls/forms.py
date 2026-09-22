from django import forms

MIN_OPTIONS = 2
MAX_OPTIONS = 5


class PollCreateForm(forms.Form):
    question = forms.CharField(label="Soru", max_length=200)
    description = forms.CharField(
        label="Açıklama (isteğe bağlı)",
        max_length=500,
        required=False,
        widget=forms.Textarea,
    )


def clean_options(raw_options):
    """Ham seçenek metinlerini doğrular. (temiz_liste, hata_mesajı) döner."""
    cleaned = [text.strip() for text in raw_options if text.strip()]

    if len(cleaned) < MIN_OPTIONS or len(cleaned) > MAX_OPTIONS:
        return None, f"Bir ankette en az {MIN_OPTIONS}, en fazla {MAX_OPTIONS} seçenek olmalı."

    seen = set()
    for text in cleaned:
        key = text.lower()
        if key in seen:
            return None, "Aynı metinli seçenekler olamaz."
        seen.add(key)

    for text in cleaned:
        if len(text) > 100:
            return None, "Her seçenek en fazla 100 karakter olabilir."

    return cleaned, None
