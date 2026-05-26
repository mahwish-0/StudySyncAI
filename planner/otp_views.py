from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from twilio.rest import Client

client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN
)

def send_otp(request):
    if request.method == "POST":
        phone = request.POST.get("phone")

        client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verifications.create(
            to=phone,
            channel="sms"
        )

        request.session["phone"] = phone
        return redirect("verify_otp")

    return render(request, "planner/send_otp.html")


def verify_otp(request):
    if request.method == "POST":
        code = request.POST.get("otp")
        phone = request.session.get("phone")

        result = client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verification_checks.create(
            to=phone,
            code=code
        )

        if result.status == "approved":
            username = phone.replace("+", "")
            user, created = User.objects.get_or_create(username=username)
            login(request, user)
            return redirect("home")

    return render(request, "planner/verify_otp.html")
