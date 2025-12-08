# services/guest_invitation_service.py
from django.core.mail import send_mass_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor


class GuestInvitationService:
    _executor = ThreadPoolExecutor(max_workers=2)

    @staticmethod
    def send_invitations_async(event_id):
        GuestInvitationService._executor.submit(
            GuestInvitationService._send_invitations_task,
            event_id
        )

    @staticmethod
    def _send_invitations_task(event_id):
        try:
            GuestInvitationService.send_invitations(event_id)
        except Exception as e:
            print(f"Erro ao enviar convites para evento {event_id}: {e}")

    @staticmethod
    def send_invitations(event_id):
        try:
            from ..models import Event, EventGuest

            event = Event.objects.filter(id=event_id).only(
                'id', 'title', 'start_datetime', 'location', 'description'
            ).first()
            
            if not event:
                return
            
            guests = EventGuest.objects.filter(
                event_id=event_id,
                invitation_sent=False
            ).only('id', 'email')
            
            if not guests:
                return
            
            # Prepara emails em lote
            emails = []
            guest_ids = []
            
            for guest in guests:
                subject = f"Convite para o evento: {event.title}"
                
                message_lines = []
                message_lines.append(f"Você foi convidado para o evento: {event.title}\n")
                
                if event.description:
                    message_lines.append(f"{event.description}\n")
                
                message_lines.append(f"📅 Data e Hora: {event.start_datetime.strftime('%d/%m/%Y às %H:%M')}\n")
                
                if event.location:
                    message_lines.append(f"📍 Local: {event.location}\n")
                
                message_lines.append("Aguardamos sua presença!")
                
                message = "\n".join(message_lines)
                
                emails.append((
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [guest.email]
                ))
                guest_ids.append(guest.id)
            
            # Envia todos os emails de uma vez
            if emails:
                try:
                    send_mass_mail(emails, fail_silently=False)
                    
                    # Atualiza todos os convidados de uma vez
                    with transaction.atomic():
                        EventGuest.objects.filter(id__in=guest_ids).update(
                            invitation_sent=True,
                            invitation_sent_at=timezone.now()
                        )
                        
                except Exception as e:
                    print(f"Erro ao enviar email: {e}")
                    
        except Exception as e:
            print(f"Erro geral: {e}")