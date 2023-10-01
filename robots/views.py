# попробую переписать api endpoint в классовой парадигме
from datetime import datetime
import json
from django.db.models.query import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.db.models import Count
from .models import Robot
from .utils import generate_xlsx_response_from_objects


class RobotsJsonResponse:
    # сгенерированный токен для API
    API = 'z+i9xkx@v)jea_-jyq^lzc2@%j%xupvja^!q07y5!1rl+(d9#e'

    @staticmethod
    def render_as_json(data):
        """
        :returns a serialized context .
        """
        if not isinstance(data, dict):  # словарь не нужно сериализовывать
            model_objects = data if isinstance(data, QuerySet) else [data]
            data = json.loads(serializers.serialize('json', model_objects, indent=2))
        return JsonResponse(data, safe=False)

    @staticmethod
    def decode_request_body(request):
        """:returns deserialized body of request"""
        decoded_body = json.loads(request.body.decode("utf-8"))
        assert isinstance(decoded_body, dict), 'допускается только словарь'
        assert set(decoded_body.keys()).issubset({'serial', 'model', 'version', 'created'}), 'Неизвестные поля'
        return decoded_body

    @staticmethod
    def validate(robot):
        try:
            robot.full_clean()
            robot.save()
            return robot
        except ValidationError as error:
            return {'status': 'failure', 'code': 404, 'message': '\n'.join(*error.message_dict.values())}

    def check_api(self, request):
        try:
            given_api = request.headers['x-api-key']
            if self.API != given_api:
                return False
            return True
        except KeyError:
            return False


@method_decorator(csrf_exempt, name='dispatch')
class RobotsList(RobotsJsonResponse, View):
    model = Robot
    http_method_names = ['get', 'post']

    def get(self, request):
        robots = self.model.objects.all()
        return self.render_as_json(robots)

    def post(self, request):
        if self.check_api(request):
            decoded_body = self.decode_request_body(request)
            if 'serial' not in decoded_body.keys():
                model, version = decoded_body['model'], decoded_body['version']
                decoded_body['serial'] = f"{model}-{version}"
            else:
                # приоритет отдаем серии, даже если serial и version были переданы оба, но разные, то мы смотрим лишь serial
                decoded_body['model'], decoded_body['version'] = decoded_body['serial'].split('-')
            decoded_body['created'] = datetime.strptime(decoded_body['created'], '%Y-%m-%d %H:%M:%S')
            created_robot = self.model(**decoded_body)
            return self.render_as_json(self.validate(created_robot))
        else:
            return self.render_as_json({'status': 'failure',
                                        'code': 403, 'message': 'access denied'})


class RobotDetail(RobotsJsonResponse, View):
    model = Robot
    http_method_names = ['get', 'patch', 'delete']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.robot = self.model.objects.filter(id=self.kwargs['id'])[0]
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id):
        return self.render_as_json(self.robot)

    def patch(self, request, id):
        if self.check_api(request):
            decoded_body = self.decode_request_body(request)
            for k, v in decoded_body.items():
                setattr(self.robot, k, v)
            if 'serial' not in decoded_body.keys():
                self.robot.serial = f'{self.robot.model}-{self.robot.version}'  # переопределяем серию
            else:
                self.robot.model, self.robot.version = decoded_body['serial'].split('-')
            return self.render_as_json(self.validate(self.robot))
        else:
            return self.render_as_json({'status': 'failure',
                                        'code': 403, 'message': 'access denied'})

    def delete(self, request, id):
        if self.check_api(request):
            self.robot.delete()
            return self.render_as_json({'status': 'success',
                                        'code': 204, 'message': 'the robots has been successfully deleted'})
        else:
            return self.render_as_json({'status': 'failure',
                                        'code': 403, 'message': 'access denied'})


@method_decorator(csrf_exempt, name='dispatch')
class RobotsSummary(View):
    model = Robot
    http_method_names = ['get']

    def get(self, request):
        year_now, week_now = datetime.today().isocalendar()[:2]  # год и номер недели
        week = int(request.GET.get('week')) if bool(request.GET.get('week')) else -1  # по умолчанию прошлая неделя
        year = int(request.GET.get('year')) if bool(request.GET.get('week')) else year_now
        robots = self.model.objects.all()
        robots_at_given_week = robots.filter(created__week=week_now + week,
                                             created__year=year)

        if not robots_at_given_week.exists():
            return HttpResponse(status=404)

        grouped_query = robots_at_given_week.values('model', 'version') \
            .annotate(per_week=Count('id')).order_by('model')
        distinct_models = Robot.objects.all().values_list('model', flat=True).distinct()
        return generate_xlsx_response_from_objects(grouped_query, 'model', distinct_models)
