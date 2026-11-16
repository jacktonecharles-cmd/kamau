from django import forms
from .models import Booking, PaymentProof, ContactMessage, NewsletterSubscriber
from django import forms
from django.utils import timezone

from .models import Booking, PaymentProof, ContactMessage, NewsletterSubscriber


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['full_name', 'email', 'phone', 'service', 'technician',
                  'date', 'time', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError("Please choose a date that is today or later.")
        return date


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ['customer_name', 'phone', 'service_name', 'amount_paid',
                  'transaction_code', 'screenshot']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']


