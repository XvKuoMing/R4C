# R4C
API-сервис, который разделен на три приложения.
<br />
! Проект не использует DRF
<br />
! PR для каждой задачи лежит в файле tasks.md

## Robots
Приложение хранит в себе всю информацию о произведенных роботах.
Все **не** GET запросы требует указания api-токена в header запроса:
```
{
  "x-api-key":"z+i9xkx@v)jea_-jyq^lzc2@%j%xupvja^!q07y5!1rl+(d9#e"
}
```
<br />
! Данный механизм защиты лишь демонстрация как можно ограничить доступ к точкам API

### GET /api/robots
Сервис выдает список всех произведенных роботов

### POST /api/robots
Сервис принимает JSON с указанием информации о роботе и создает робота в БД.
<br />
Данные можно присылать в двух вариантах:
<br />
I. C указанием серии --> модель и версия робота заполняться автоматически
<br />
II. С указанием модели И версии --> сериа заполниться автоматически
!Поэтому форма данных следующая: Указать serial ИЛИ (model И version), и created

### GET /api/robots/{robot's id}
Сервис выдает робота с указанным ключом БД

### PATCH /api/robots/{robot's id}
Сервис принимает JSON с указанием полей для обновления и обновляет робота с указанным ключом БД.
Данные можно присылать в двух вариантах:
<br />
I. С указанием серии --> модель или версия поменяются автоматически
<br />
II. С указанием модели ИЛИ версии --> серия обновится автоматически

### DELETE /api/robots/{robot's id}
Сервис удаляет робота с указанным ключом БД

### GET /api/robots/report
Сервис генерирует excel файл, с котором каждый лист содержит сводную таблицу количества произведенных роботов конкретной модели и ее версий.
<br />
Запрос принимает два опциональных параметра: *week* и *year*.
<br />
**year** — номер текущего года. По умолчанию стоит 2023
<br />
**week** — номер недели относительно текущей. По умолчанию стоит -1, что означает прошлая неделя. Положительное числа — будущие недели, 0 — текущая.
<br />
Такой относительный отчет недель позволяет руковителю не думать о том, чтобы постоянно обновлять параметр ссылки.
Кроме того, в будущем можно будет вводить данные о еще не произведенных роботов, тогда с помощью положительных чисел для week, руководитель сможет мотреть сводные по роботам, которые только планируется сделать

## Customers
Приложение позволяет пользователю сохранить почту в БД (также ее можно удалить).
Так как пользователю нужно лишь уведомление о поставке роботов (при их отсутсвии), автор решил использовать session-based authentification.
Почта сохраняется в сессии пользователя и в БД.

### POST /login
Принимает JSON с единственным ключом: email. Записывает этот email в БД и хранить в сессии. Если Email — некорректный, то выдает ошибку

### GET /login
Выдает JSON с указанием, email зарегистрированного пользователя или c сообщением о том, что пользователь не указал еще почту

### POST /logout
Принимает JSON с единственным ключом: sure: bool. При sure==True, удаляем email из сессии и из БД

## Orders
Приложение хранит список роботов, которые еще нет, но пользователи их ждут. Отправляет email при поступлении робота

### GET /api/robots/{robot's serial}
Сервис выдает пользователю робота с указанной серией. Если не находит, то записывает пользователя и его заказ в список ожиданий (orders).
При поступлении (когда технические специалисты создадут этого робота), отправляет пользователю email-письмо от "beilassistant@gmail.com"

