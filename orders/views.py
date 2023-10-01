import json
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models.query import QuerySet
from robots.models import Robot
from customers.models import Customer
from .models import Order


@require_http_methods(['GET'])
def get_robots(request, serial):
    serial = serial.strip()
    if 'email' in request.session.keys():
        try:
            robots = Robot.objects.get(serial=serial)
            robots = [robots] if not isinstance(robots, QuerySet) else robots
            data = json.loads(serializers.serialize('json', robots, indent=2))
            return JsonResponse(data, safe=False)
        except Robot.DoesNotExist:
            customer = Customer.objects.get(email=request.session['email'])
            if not Order.objects.filter(robot_serial=serial).exists():
                Order.objects.create(customer=customer, robot_serial=serial)
            return HttpResponse(f'К сожалению, мы еще не выпустили робота серии {serial}.\n'
                                 'Как только он появится, мы сразу же сообщим вам по почте ', status=404)
    else:
        JsonResponse({"status": "failure", 'code': 404, 'message': 'no credentials'})
