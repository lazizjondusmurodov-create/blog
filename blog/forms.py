from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Aloqa sahifasidagi forma.

    Yashirin 'website' maydoni — bot tuzog'i (honeypot): odam uni ko'rmaydi,
    bot esa to'ldiradi. To'ldirilgan bo'lsa xabar saqlanmaydi.
    """

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
        }),
        label='',
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ismingiz',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@misol.uz',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Xabar mavzusi',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': 'Xabaringiz...',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError(
                "Ism kamida 2 ta belgidan iborat bo'lishi kerak."
            )
        return name

    def clean_subject(self):
        subject = self.cleaned_data['subject'].strip()
        if len(subject) < 3:
            raise forms.ValidationError(
                "Mavzu kamida 3 ta belgidan iborat bo'lishi kerak."
            )
        return subject

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError(
                "Xabar kamida 10 ta belgidan iborat bo'lishi kerak."
            )
        return message

    def clean_website(self):
        """Honeypot: bu maydon faqat bot tomonidan to'ldiriladi."""
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam aniqlandi.')
        return ''
