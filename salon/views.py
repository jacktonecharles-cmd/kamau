import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookingForm, PaymentProofForm, ContactForm, NewsletterForm
from .models import (
    ServiceCategory, Service, Technician, GalleryImage, GalleryCategory,
    Testimonial, Booking, PaymentProof, ContactMessage, NewsletterSubscriber,
)

logger = logging.getLogger(__name__)

POLICIES = {
    'cancellation': ('Cancellation Policy',
                     'Please give us at least 24 hours notice to cancel or reschedule your appointment.'),
    'privacy': ('Privacy Policy',
                'We only use your details to manage your bookings and never sell your data.'),
    'terms': ('Terms of Service',
              'By booking with Kamau Nails you agree to our appointment and payment terms.'),
}

FAQS = [
    ('How do I book?', 'Use the booking page, choose a service, date and time.'),
    ('How do I pay?', 'Send payment by M-Pesa, then upload your proof on the payment page.'),
    ('Can I reschedule?', f'Yes, call us on {settings.SALON_PHONE} at least 24 hours ahead.'),
]


def _notify(subject, body, recipients):
    """Send an email without ever crashing the page if mail fails."""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    except Exception:
        logger.exception("Email sending failed")


# ---------------- Public pages ----------------

def home(request):
    return render(request, 'salon/home.html', {
        'featured_services': Service.objects.filter(is_featured=True).select_related('category')[:6],
        'technicians': Technician.objects.all()[:4],
        'testimonials': Testimonial.objects.filter(is_published=True)[:6],
        'gallery_images': GalleryImage.objects.all()[:8],
        'newsletter_form': NewsletterForm(),
    })


def about(request):
    return render(request, 'salon/about.html', {'technicians': Technician.objects.all()})


def services(request):
    return render(request, 'salon/services.html', {
        'categories': ServiceCategory.objects.prefetch_related('services'),
    })


def service_detail(request, slug):
    service = get_object_or_404(Service.objects.select_related('category'), slug=slug)
    related = Service.objects.filter(category=service.category).exclude(pk=service.pk)[:3]
    return render(request, 'salon/service_detail.html', {'service': service, 'related': related})


def team(request):
    return render(request, 'salon/team.html', {'technicians': Technician.objects.all()})


def gallery(request):
    category = request.GET.get('category', '')
    images = GalleryImage.objects.all()
    if category in GalleryCategory.values:
        images = images.filter(category=category)
    else:
        category = ''
    return render(request, 'salon/gallery.html', {
        'images': images,
        'categories': GalleryCategory.choices,
        'active_category': category,
    })


def booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            obj = form.save()
            request.session['last_booking_id'] = obj.pk
            _notify(
                "We received your booking - Kamau Nails",
                f"Hi {obj.full_name},\n\nThanks for booking {obj.service.name} on "
                f"{obj.date} at {obj.time:%H:%M}. We will confirm shortly.\n\n"
                f"Call us on {settings.SALON_PHONE} if you need to make changes.",
                [obj.email],
            )
            _notify(
                "New booking",
                f"{obj.full_name} ({obj.phone}) booked {obj.service.name} on {obj.date} at {obj.time:%H:%M}.",
                [settings.SALON_ADMIN_EMAIL],
            )
            return redirect('booking_success')
    else:
        initial = {}
        slug = request.GET.get('service')
        if slug:
            svc = Service.objects.filter(slug=slug).first()
            if svc:
                initial['service'] = svc.pk
        form = BookingForm(initial=initial)
    return render(request, 'salon/booking.html', {'form': form})


def booking_success(request):
    booking_obj = None
    booking_id = request.session.get('last_booking_id')
    if booking_id:
        booking_obj = Booking.objects.filter(pk=booking_id).select_related('service', 'technician').first()
    return render(request, 'salon/booking_success.html', {'booking': booking_obj})


def payment(request):
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            booking_id = request.session.get('last_booking_id')
            if booking_id:
                proof.booking = Booking.objects.filter(pk=booking_id).first()
            proof.save()
            _notify(
                "New payment proof submitted",
                f"{proof.customer_name} paid KES {proof.amount_paid} (code {proof.transaction_code}).",
                [settings.SALON_ADMIN_EMAIL],
            )
            messages.success(request, "Payment proof received. We will verify it shortly.")
            return redirect('payment')
    else:
        form = PaymentProofForm()
    return render(request, 'salon/payment.html', {'form': form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save()
            _notify(
                f"New contact message from {msg.name}",
                f"From: {msg.name} <{msg.email}>\n\n{msg.message}",
                [settings.SALON_ADMIN_EMAIL],
            )
            messages.success(request, "Thanks! Your message has been sent.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'salon/contact.html', {'form': form})


@require_POST
def newsletter_signup(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        NewsletterSubscriber.objects.get_or_create(email=form.cleaned_data['email'])
        messages.success(request, "You are subscribed. Thank you!")
    else:
        messages.error(request, "Please enter a valid email address.")
    return redirect(request.META.get('HTTP_REFERER') or 'home')


def faq(request):
    return render(request, 'salon/faq.html', {'faqs': FAQS})


def policy(request, slug):
    if slug not in POLICIES:
        from django.http import Http404
        raise Http404("Policy not found")
    title, body = POLICIES[slug]
    return render(request, 'salon/policy.html', {'title': title, 'body': body})


# ---------------- Custom staff dashboard ----------------
# Staff must be logged in via /admin/login/ (is_staff = True).

@staff_member_required
def admin_dashboard(request):
    stats = {
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'total_payments': PaymentProof.objects.count(),
        'unverified_payments': PaymentProof.objects.filter(is_verified=False).count(),
        'messages': ContactMessage.objects.count(),
    }
    return render(request, 'salon/admin_dashboard.html', {
        'stats': stats,
        'bookings': Booking.objects.select_related('service', 'technician')[:100],
        'payments': PaymentProof.objects.all()[:100],
        'contact_messages': ContactMessage.objects.all()[:100],
        'status_choices': Booking.STATUS_CHOICES,
    })


@staff_member_required
@require_POST
def update_booking_status(request, booking_id):
    booking_obj = get_object_or_404(Booking, pk=booking_id)
    status = request.POST.get('status')
    if status in dict(Booking.STATUS_CHOICES):
        booking_obj.status = status
        booking_obj.save(update_fields=['status'])
        messages.success(request, f"Booking #{booking_obj.pk} updated to {status}.")
    else:
        messages.error(request, "Invalid status.")
    return redirect('admin_dashboard')


@staff_member_required
@require_POST
def update_payment_status(request, payment_id):
    proof = get_object_or_404(PaymentProof, pk=payment_id)
    proof.is_verified = request.POST.get('is_verified') == '1'
    proof.save(update_fields=['is_verified'])
    messages.success(request, f"Payment #{proof.pk} marked "
                              f"{'verified' if proof.is_verified else 'awaiting verification'}.")
    return redirect('admin_dashboard')