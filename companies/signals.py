from django.dispatch import Signal, receiver
from authentication.utils import Utils
from companies.models import Company

company_update = Signal()

@receiver(company_update)
def company_update_reciever(sender, company, **kwargs):
    emails_to_send = [record.user_id.email for record in 
                      company.subscription_set.filter(get_email_newsletter=True)]
    print(emails_to_send)
