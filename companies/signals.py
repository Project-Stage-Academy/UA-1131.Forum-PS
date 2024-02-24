from django.dispatch import Signal, receiver
from forum.tasks import email_sender_celery
from forum.settings import EMAIL_HOST_USER

company_update = Signal()

@receiver(company_update)
def company_update_reciever(sender, company, **kwargs):
    emails_to_send = [record.investor.email for record in 
                      company.subscription_set.filter(get_email_newsletter=True)]
    for email in emails_to_send:
        data = {'email_subject': 'Update in followed company',
                'email_body': 'Dear user, we would like to inform you about the updates in the company you are following.',
                'from_email': EMAIL_HOST_USER,
                'to_email': email            
                } 
        email_sender_celery.delay(data)
