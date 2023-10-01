from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Customer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json

@method_decorator(csrf_exempt, name='dispatch')
class CustomerLogIn(View):
    model = Customer
    http_method_names = ['get', 'post']

    def post(self, request):
        email = json.loads(request.body.decode("utf-8"))['email']
        try:
            validate_email(email)
            if not self.model.objects.filter(email=email).exists():
                self.model.objects.create(email=email)
            request.session['email'] = email
            result = {'status': 'success', 'code': 200, 'message': 'You have been successfully signed'}
        except ValidationError as error:
            result = {'status': 'failure', 'code': 400, 'message': error.message}
        return JsonResponse(result)

    def get(self, request):
        if 'email' in request.session.keys():
            return JsonResponse({'status': 'success', 'email': request.session['email']})
        else:
            return JsonResponse({'status': 'failure', 'message': 'you are not logged in'})


@method_decorator(csrf_exempt, name='dispatch')
class CustomerLogOut(View):
    model = Customer
    http_method_names = ['post']

    def post(self, request):
        sure = json.loads(request.body.decode("utf-8"))['sure']
        if sure and ('email' in request.session.keys()):
            self.model.objects.get(email=request.session['email']).delete()
            request.session.pop('email')
            return JsonResponse({'status': 'success', 'code': 200, 'message': 'You have been successfully logged out'})
        else:
            return JsonResponse({'status': 'failure', 'code': 404, 'message': 'you have not been signed up in the first place'})
