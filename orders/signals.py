from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from robots.models import Robot
from .models import Order


@receiver(post_save, sender=Robot)
def notify_if_ordered_robot_is_created(sender, instance, created, **kwargs):
    if created:
        new_serial = instance.serial
        try:
            notify_users = Order.objects.filter(robot_serial__icontains=new_serial)
            users_emails = []
            for order in notify_users:
                users_emails.append(order.customer.email)
                order.delete()
            message = f'''Добрый день!\nНедавно вы интересовались нашим роботом модели {new_serial[:2]}, версии {new_serial[-2:]}.\nЭтот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами'''
            send_mail(
                subject=f'Поступление {new_serial}',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=users_emails,
                fail_silently=False
            )

        except Order.DoesNotExist:
            return HttpResponse(f'Нет заказа для {new_serial}', status=404)

