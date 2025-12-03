from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import threading


class GuestInvitationService:
    @staticmethod
    def send_invitations_async(event):
        thread = threading.Thread(target=GuestInvitationService.send_invitations, args=(event,))
        thread.daemon = True
        thread.start()

    @staticmethod
    def send_invitations(event):
        guests = event.guests.filter(invitation_sent=False)

        for guest in guests:
            GuestInvitationService.send_invitation_email(event, guest)
            guest.invitation_sent = True
            guest.invitation_sent_at = timezone.now()
            guest.save()

    @staticmethod
    def send_invitation_email(event, guest):
        subject = f"Convite para o evento: {event.title}"
        message = f"""
        Olá!

        Você foi convidado para o evento: {event.title}

        Data: {event.start_datetime.strftime('%d/%m/%Y %H:%M')}
        Local: {event.location or "Não informado"}

        Por favor, confirme sua presença respondendo a este email.

        Atenciosamente,
        Equipe EventU
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [guest.email],
            fail_silently=False,
        )
