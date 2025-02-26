# from django.core.mail import EmailMessage
#
# from django.conf import settings
# from django.contrib.auth.tokens import default_token_generator
# from django.template.loader import render_to_string
# from django.urls import reverse
#
#
# def send_email_confirmation(user, code):
#     subject = "Confirm Your Email Address"
#     html_/message = render_to_string('auth/email_confirmation.html', {
#         'user': user,
#         'code': code,
#     })
#
#     email = EmailMessage(subject,
#                          message,
#                          settings.EMAIL_HOST_USER,
#                          [user.email])
#     email.content_subtype = 'html'
#     email.send()


from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse


def send_email_confirmation(user):
    # Generate the confirmation token for the user
    token = default_token_generator.make_token(user)

    # Construct the confirmation link
    confirmation_url = reverse('email_confirmation', args=[user.pk, token])

    # Create the subject and message for the email
    subject = "Confirm Your Email Address"
    html_message = render_to_string('auth/email_confirmation.html', {
        'user': user,
        'confirmation_url': confirmation_url,
    })

    # Send the email
    email = EmailMessage(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [user.email]
    )
    email.content_subtype = 'html'
    email.send()
