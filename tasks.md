# Task 1. От технического специалиста компании.
Создать API-endpoint, принимающий и обрабатывающий информацию в формате JSON. 
В результате web-запроса на этот endpoint, в базе данных появляется запись 
отражающая информацию о произведенном на заводе роботе. 

_**Примечание от старшего технического специалиста**_: 
Дополнительно предусмотреть валидацию входных данных, на соответствие существующим в системе моделям.

Пример входных данных:

```{"model":"R2","version":"D2","created":"2022-12-31 23:59:59"}```

```{"model":"13","version":"XS","created":"2023-01-01 00:00:00"}```

```{"model":"X5","version":"LT","created":"2023-01-01 00:00:01"}```


# Решение 1.
<br />
Так как всю информацию нужно передавать в формате JSON, для начала в папке view.py был создан класс RobotsJsonResponse.
<br />
В нем были прописаны методы для сериализации данных в JSON и декодирования данных из JSON.
<br />
В дальнейшем были созданы еще два класса: RobotsList и RobotDetail, которые наследовались от RobotJsonResponse
<br />
Класс RobotsList допускает два HTTP метода: GET и POST по следующему API: /api/robots
<br />
  a. При GET RobotsList выдает список произведенных роботов в формате JSON.
<br />
  b. При POST RobotsList принимает JSON, ключи которого — поля модели Robots.
<br />
Данные можно прислать в двух вариантов:
<br />
  i. Указать model, version и created (дата в формате %Y-%m-%d %H:%M:%S), тогда serial заполнится автоматически
<br />
  ii. Указать serial и created, тогда model и version заполняться автоматически (при указании model или version вместе с serial, RobotDetail отдаст приоритет serial)
5. Класс RobotDetail допускает три метода: GET, PATCH, DELETE по следующему API: /api/robots/<id>, где  type id: int
<br />
  a.  При GET RobotDetail выдает JSON с информацией о роботе с ключом id
<br />
  b.  При PATCH RobotDetail принимает JSON с каким-либо полем из (serial, model, version, created) и обновляет данные в роботе с указанным id.
Данные снова можно прислать в двух вариантах:
<br />
  i. Указать serial, тогда RobotDetail обновит и model, version
<br />
  ii. указать model или version, тогда RobotDetail обновит serial (при указании model или version вместе с serial, RobotDetail отдаст приоритет serial)
<br />
  c.  При DELETE RobotDetail удаляет робота с указанным id

# Task 2. От директора компании
**User Story**: Я как директор хочу иметь возможность скачать по прямой ссылке Excel-файл со сводкой по суммарным показателям производства роботов за последнюю неделю. 

_**Примечание от менеджера**_. Файл должен включать в себя несколько страниц, на каждой из которых представлена информация об одной модели, но с детализацией по версии. 

Схематично для случая с моделью "R2":

```
 __________________________________
|Модель|Версия|Количество за неделю|
 __________________________________
|  R2  |  D2  |       32           |
 __________________________________
|  R2  |  A1  |       41           |
              ...
              ... 
              ...
|  R2  |  С8  |       99           |
              ...  
```

# Решение 2. 
В приложении robots файле view.py был реалиован класс RobotsSummary.
<br />
Он принимает лишь GET запросы по следующему API: **/api/robots_report**
<br />
Также запрос принимает два ключа: week: int и year: int. Если их не указать, то RobotsSummary будет использовать текущую неделю и год.
<br />
При этом неделя определяется всегда относительно текущего дня. Если указать ?week=-1, то RobotsSummary распознает это как прошлая неделя
В то время как ?week=1 — следующая неделя.
<br />
Такая функция может быть полезна при планировании роботов. Например, в базу данных технические специалисты направляют даннные как созданных роботов, так и планиуремых.
<br />
В таком случае директор можно с помощью week=1 и week=0 (по умолчанию) узнать, сколько роботов будет сделано и сколько уже сделано
5. RobotsSummary использует библиотеку openpyxl для генерации excel файла. Он генерируется следующим образом:
<br />
    i. Сначала RobotsSummary отбирает роботов по указанным параметрам week и year
<br />
    ii. Затем RobotsSummary группирует их по модели и версии с подсчетом их количества
<br />
    iii. Далее, функция generate_xlsx_response_from_objects (из utils.py) создает excel файл с количеством листов равное количеству моделей. На каждом листе собрана информация о количестве соответствующей модели и ее версиях


# Task 3. От клиента компании.
**Job story**: Если я оставляю заказ на робота, и его нет в наличии, я готов подождать до момента появления робота. После чего, пожалуйста пришлите мне письмо.

_**Примечание от менеджера**_: Письмо должно быть следующего формата
```
Добрый день!
Недавно вы интересовались нашим роботом модели X, версии Y. 
Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами
```
где Х и Y это соответственно модель и версия робота.

_**Примечание от старшего технического специалиста**_: Постарайтесь не переопределять встроенные методы модели. Также стремитесь не смешивать контексты обработки данных и бизнес-логику. Рекомендуется использовать механизм сигналов предусмотренный в фреймворке.


# Решение 3.
За решение этой задачи отвественны сразу два приложения: customers и orders.
<br />
Customers — обеспечивает регистрацию почт пользователей
**Примечание**: чтобы не переопределять встроенные методы моделей (Customers и Orders), автор решил хранить почты пользователей в сессиях и в бд. 
<br />
Orders — выдает роботов по серии или, если их нет в наличии, записывает почту пользователя (узнает из сессии) и его заказ в список ожиданий (Orders БД)
<br />
В последующем, когда технический специалист создан ожидаемого робота, сервис отправит письмо о поступлении искомого пользователем товара.
<br />
**Отправитель**: beilassistant@gmail.com


