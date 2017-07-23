# hoROOMy parsers system

## Содержание

[Структура](#structure)<br>
[Методы сервера](#server)  
* [System](#System)
* [Parsers](#Parsers)
* [Results](#Results)
* [Statuses](#Statuses)
* [UX](#UX)
* [Map](#Map)
* [DataBase](#DataBase)
* [Stuff](#Stuff)<br>
[Классы](#Classes)
* [DataBase](#DB_class)
* [BackuppedFile](#back-file)
* [Parse](#Parse)
* [Bot](#bot)<br>
[Глобальные переменные и функции](#alertBot)<br>
[Логика ДБ](#parseit)<br>
[Запуск](#run_it)

<a name="structure"></a>
## Структура

### Root

##### .py файлы  

*app.py* -- сервер на Bottle  
*botAPI.py* -- телеграм-бот (for alerts)  
*database.py* -- методы работы с базой данных  
*driveAPI.py* -- методы Dropbox - костыль  
*parseAPI.py* -- **парсеры тут**  
*parser_class.py* -- определение класса **Parse** для оптимизации
<br>

##### Файлы для сервера  

*.gitignore*  
*procfile*  
*requirements.txt* -- используемые библиотеки  
*runtime.txt* -- версия интерпретатора
<br>

##### Прочие файлы  

*parseRes.db* -- база данных сервера  
*parser_list.json* -- список активных парсеров
<br>

### html

##### Системные  

*main.html* -- управление парсерами*//  
*main-adm.html* -- редактировать main//  
<br>

##### Для пользователя

*search.html* -- поиск по базе  
*tableRes.html* -- результаты поиска*//  
*circler.html* -- показать дом на карте*  
<br>

##### Сырое  

*metroLookAround.html* -- выводит соседние станции метро по данной (in production)*  
*stats.html* -- форма получения статистики из БД (unnecessary)  
*giveMeStats.html* -- статистика по параметрам из формы//  
<br>
```
* -- includes JS code  
// -- is rendered as a template  
```
<br>

### css  

*style.css* -- стили для *tableRes.html*
<br>

### pics  

*foto.png* -- если фотографии в объявлении отсутствуют (для *tableRes.html*)
<br>

<a name="server"></a>
## Методы сервера  

Обращения к серверу осуществляются с помощью GET-запросов. **POST запросы не используются в данном АПИ.**
<br><br>

<a name="System"></a>
### System  

Консоль администратора

<br>

************************

<br>

#### /system/  

Графический интерфейс управления парсерами. Требует ввода логина и пароля.
>Отуствует хэширование и хранение пар **логин-хэш** в базе данных. Данная функция создана только для защиты от "дураков".

Авторизация через Auth headers.
<br>

#### /system/edit  

HTML страница для редактирования блока *"Уведомления от разработчика"* в main.html -- ~~ненужная фигня~~ 
<br>

#### /system/сhangemain  

HTML из `/system/edit` посылает GET-запрос сюда для изменения блока *"Уведомления от разработчика"*  
~~Не задокументировано, так как нафиг никому не нужно~~
<br><br>

<a name="Parsers"></a>
### Parsers  

Методы управления парсерами
<br>

************************

<br>


#### /parsers/start_social  

Начать парсинг записей ВК  
**Необязательные параметры**:
* num=<int> - количество записей, которые необходимо взять у каждой группы (по умолчанию 100)
<br>

#### /parsers/start_parse  

Запустить все парсеры агрегаторов (то есть всё, кроме парсинга ВК)
**Необязательные параметры**:
* maxprice=<int> - ограничение по цене для квартир (по умолчанию 55000)
<br>

#### /parsers/special_parse  

Тестирование одного парсера:
* Для ВК: парсинг 100 записей в каждой группе
* Для других парсеров: парсинг объявлений с maxprice=15000

***Обязательные*** **параметры**:

* parser_name=<str> -- парсер, который надо протестировать

>**Значения parser_name:**
?parser_name=***vk*** -- парсинг вк
?parser_name=***<название парсера из parser_list.json>*** - запуск данного парсера

<br>

#### *ПРИМЕРЫ:*  

```python
# parse VK
# 100 posts in each community
url = "http://horoomy-parsers.herokuapp.com/start_social"
requests.get(url)   # <response 200>
requests.post(url)  # <error 405>


# start all parsers
# price less than 10000 rub/month
url = "http://horoomy-parsers.herokuapp.com/start_parse"
params = "?maxprice=10000"
requests.get(url+params)    # <response 200>


# test VK parser
url = "http://horoomy-parsers.herokuapp.com/special_parse"
params = "?parser_name=vk"
requests.get(url+params)    # <response 200>


# test irr.ru parser
url = "http://horoomy-parsers.herokuapp.com/special_parse"
params = "?parser_name=irr"
requests.get(url+params)    # <response 200>

```
<br><br>
<a name="Results"></a>
### Results

<br>

************************

<br>

#### /results/giveMeResults/<parser_name>  

Возвращает [json с данными](resultsFormat), полученными указанным парсером.  
*Версия с большим количеством параметров --* [/giveMeFlats](giveMeFlats)
<br>

#### /results/clearAll  

Очищает таблицы Results и Snimu в [базе данных](databaseStructure).
<br>

#### Примеры
```python
# get existing results
url = "http://horoomy-parsers.herokuapp.com/results/giveMeResults/"  
parser = "realEstate"  
r = requests.get(url+parser).text  
print(r)    # "[(''), (''), ...]"

# clear results
url = "http://horoomy-parsers.herokuapp.com/results/clearAll"  
r = requests.get(url)   # <response 200>

# try to get results
url = "http://horoomy-parsers.herokuapp.com/results/giveMeResults/"  
parser1 = "realEstate"  
parser2 = "rentooki"
r1 = requests.get(url+parser1).text
r2 = requests.get(url+parser2).text
print(r1)    # "[]"
print(r2)    # "[]"
```
<br><br>
<a name="Statuses"></a>
### Statuses  

Методы проверки состояния парсеров
*****
***Cтатус может принимать следующие значения:***
* *натуральное число* -- парсер ещё не завершил работу, возвращается кол-во обработанных страниц/объявлений (зависит от парсера)
* *last updated on: YYYY.MM.DD HH:MM:SS*
* *last updated on: never* -- в бд нет данных этого парсера
*****

<br>

************************

<br>

#### /statuses/plist  

Возвращает список активных парсеров *(parser_list.json)*
<br>

#### /statuses/giveMeStatus/<parser>  

Возвращает статус для данного парсера.
<br>

#### Примеры  

```python
# list active parsers
url = "http://horoomy-parsers.herokuapp.com/statuses/plist"
parser_list = requests.get(url).text
print(parser_list)  # ["cian", "irr", "realEstate", ...]

# get a parser's status
url = "http://horoomy-parsers.herokuapp.com/statuses/giveMeStatus/"
parser = "cian"
status = requests.get(url+parser).text
print(status)   # "133"
```
<br><br>

<a name="UX"></a>
### User Experience  
<br>

*********************

<br>

#### /search  

Возвращает search.html
<br>

#### /giveMeFlats  

Возвращает список из 20 объектов (квартиры, комнаты) по данным параметрам

**Необязательные параметры:**
* dealType -- тип объекта
>Значения dealType:  
***Flat*** -- квартира  
***Room*** -- комната  
**По умолчанию:** dealType=Room  
* metro -- станция метро (не указано => возвращаются кв. в районе любого метро)
>Значения metro:  
Название любой станции метро Москвы

**Список всех значений приведён в search.html**
* room_num -- комнатность (не указано => любая)
>Значения room_num:  
***n*** - n-комнатная квартира (n от 1 до 3)

* cost -- ориентировочная цена, руб (не указано => любая)
* page -- страница (по умолчанию - 1)
* html -- формат вывода данных
>Значения html:  
***off*** -- вывод json-списка  
***on*** -- возврат обработанного шаблона tableRes.html  
***count*** -- возврат кол-ва результатов поиска

**По умолчанию: html=on**
<br>

#### Примеры:  

```python
url = "http://horoomy-parsers.herokuapp.com/statuses/giveMeFlats"
r = requests.get(url)
print(r.text)   # tableRes.html containing first 20 room offers

params = "?metro=Славянский бульвар&room_num=1&cost=20000&dealType=Flat"
r = requests.get(url+params)
print(r.text)   # tableRes.html containing 1-room flats in Славянский бульвар area that cost ~20000 rub (first 20)

params += "&page=2"
r = requests.get(url+params)
print(r.text)   # show 20th to 40th flats for the same search query

params = "?room_num=2&dealType=Room"
r = requests.get(url+params)
print(r.text)   # we get rooms, the room_num parameter is ignored!!!

# results count
params += "&html=count"
r = requests.get(url+params)
print(r.text)   # "1234"

# results json
params = "room_num=2&html=off"
r = requests.get(url+params)
print(r.text)   # "{...}"

# results html
params = "room_num=2"
r = requests.get(url+params)
print(r.text)   # "<html>...</html>"

```
[Read more about rendering tableRes.html](rendering)
[Read more about the json](resultsFormat)

<br><br>

<a name="map"></a>
### Map  

<br>

************************

<br>

#### /map/geolocate  

Возвращает circler.html с указанием места на карте

***Обязательные*** **параметры**:
* loc - строка типа "<lo.ngitude>,<la.titude>"

Если не указан парметр loc, возникает **Error 500**
<br><br>

<a name="DataBase"></a>
### DataBase

<br>

******************

<br>

#### /db/download  

Загрузка базы данных на устройство
<br>

#### /db/sync  

[Выгрузка базы данных в dropbox](dropbox)
<br><br>

<a name="Stuff"></a>
### Stuff  

<br>

************************

<br>

#### /pics/<filename>  

Получить картирку по названию из каталога ./pics/
<br>

#### /css/<filename>  

Получить stylesheet по названию из каталога ./css/
<br><br><br>

<a name="Classes"></a>
## Классы  
<br><br>

<a name="DB_class"></a>
### DataBase (database.py)  

```python
class DataBase:
    name = ''
    _db_connection = None
    _db_cur = None
```

<br>

************************

<br>

<a name="fetch_db"></a>
#### .query(self, query)  

Executes a single SQL statement.  
<br>

#### .fetch(self, query)  

Returns the result of a statement execution.  
<br>

#### .format(self)  

Create [all tables]('db_tables')  
<br>

#### .delete_table(self, table)  

Clear all results in a table  
<br>

#### `__del__`(self)  

Close DataBase connection.  
<br>

#### Пример:
```python
# create a db connection
db = DataBase("test.db")

# create a table
cmnd = """
CREATE TABLE Snimu (
number INTEGER PRIMARY KEY,
the_key TEXT,
the_value TEXT);
"""
db.query(cmnd)

# select everything from the table
res = db.fetch("SELECT * FROM Snimu")
print(str(res))   # [("", "", ""), ("", "", ""), ...]

# try formatting the db
db.format()
# EXCEPRION!!! Table Snimu already exists!!!
# Once a table is created, you can't change its structure
# Delete the db manually and create a new one

# close the connection
del db

```
<br><br>

### BackuppedFile (driveAPI.py)  
<a name="back-file"></a>

Все изменения в файлах, хранящихся на heroku, сбрасываются при перезагрузке сервера (перезагрузка осуществляется автоматически не менее одного раза в день).
Чтобы сохранять и восстанавливать эти изменения, введён класс BackuppedFile.
```python
class BackuppedFile:
    filename = ''       # filename on the device
    DBXfilename = ''    # filename in the cloud
```

<br>

************************

<br>

#### .upload(self)  

Выгрузить файл в Dropbox - сохранить изменения.  
<br>

#### . sync(self)  

Загрузить файл с Dropbox на устройство - восстановить изменения.
<br>  

#### Пример:  

```python
# before server run, beggining of the .py file
myFile = BackuppedFile("myFile.txt")
myFile.sync()   # restore the file

server_run()

...

change_smth_in_myFiletxt()
myFile.upload() # save changes to the file
```
<br><br>

<a name="Parse"></a>
### Parse (parser_class.py)  

```python
class Parse:
    name = ""
    db = None   # each parser has its own db connection to enable multithreading
```

<br>

*********************

<br>

#### .write_status(self, status=<int>)  

Вносит новый статус (количество обработанных объявлений) в таблицу `Statuses` бд для данного парсера (self.name).  
<br>

#### .add_date(self)  

Пишет `last updated on: YYYY.MM.DD HH:MM:SS` в таблицу `Statuses` бд.  
<br>

#### .get_results(self)  

Возвращает результаты, полученные этим парсером  
<br>

#### .get_status(self)  

Возвращает статус данного парсера  
<br>

#### .append(self, data, useHash=False)  

Добавляет данные из словаря `data` в таблицу `Results`.  

```python
if useHash:
    unique_id = hash(data['descr'])
else:
    unique_id = getUID(data)
```
<br>

#### .append_snimu(self, data)  

Добавляет данные из `data` в таблицу `Snimu`.
**Всегда используется hash() для получения идентификатора объявления**  
<br>

#### `__del__`(self)  

Закрывает соединение с `self.db`.  
<br>

#### Пример:  

```python
# create a Parse object
p = Parse('cian')

# parse each flat
for counter, url in enumerate(urls):
    # get data
    data = get_offer_from_cian(url)
    # insert data into the db
    p.append(data)
    # write the number of the links processed
    p.write_status(counter)
    # print out number of the links processed
    print(p.get_status())
    
# change the status to "last updated on ..."
p.add_date()
# print all the data parsed
print(p.get_results())
# close the database connection
del p
```
<br>

<a name="bot"></a>
### Bot (BotAPI.py)

API для уведомлений в telegram.

```python
class Bot:
    full_link = ""     # link to the chat the bot will write to

    def __init__(self, chat_id):    # recieve chat_id and generate full_link
        self.full_link = "https://api.telegram.org/bot332143024:AAFXvkc397uXcvN3HgbiKQ0GTaNXKf-H-zs/%s?chat_id="+chat_id

```
<br>
*****************************
<br>

#### .sendMessage(text)
Отправляет сообщение

<br>

## Глобальные переменные и функции

<a name="alertBot"></a>
#### alertBot
Глобальная переменная - объект класса [Bot](#bot), который пишет сообщения в чат со мной:D

#### alertExc()
Функция, которая при вызове отправляет traceback в чат со мной:D

```python
try:
    some_lagging_func(arg1, arg2)    # Exception ...
except:
    alertExc()    # I recieve exception info in my telegram

# decorator for functions with no arguments
@tgExcnoargs
def some_other_func():
    raise RuntimeError  # an exception occurs => I get a message
```

#### DBcon
Глобальный DataBase connection (используется там, где не используется multithreading)

#### PARSER_LIST
Список активных парсеров

#### FORMAT_DIC
Cловарь для уведомлений от разработчика

<a name="parseit"></a>
#### parse_it(parser, maxprice)
Запуск парсера по имени (parseAPI.py, line 1850)

## Логика ДБ

На сервере используется библиотека sqlite3 для управления бд.
Файл базы данных: `parseRes.db`
<br>


### Использование класса BackuppedFile

<br>  

*Причина использования sqlite*: хероку предоставляет подключение к postgresql базам, но предупреждает о периодической смене `database credentials`; также в тестовом тарифном плане ограничение - 1000 строк (при основной таблице Results ~ 5000 строк и Snimu ~ 2000 строк). Решение -- хранение sqlite3 бд прямо на сервере.  

*Недостатки использования sqlite:* при каждой перезагрузке сервера все файлы сбрасываются до первоначального состояния. Перезагрузка осуществляется минимум раз в сутки. Таким образом, каждые сутки все таблицы будут вновь и вновь очищаться :(  

*Костыли:* использование [BackuppedFile](#back-file) для сохранения последней версии дб на Dropbox и скачивании этой версии перед запуском сервера.

<br>  

### Структура БД  

```javascript
                        |------------------ Results
                        |------------------ Snimu
`parseRes.db` ----------|
                        |------------------ Statuses
                        |------------------ alerts
```  

#### Таблица Results  
Объявления типа **"сдам"**

|ind|Столбец|Тип данных|Комментарии|
|-----|----|----|--------|
|0|hash|TEXT|См [хэширование](hash) |
|1|cost|INTEGER| |
|2|room_num|INTEGER|0 - комната, -1 - койко-место (experimental)|
|3|area|INTEGER| |
|4|phone|TEXT|Код+телефон без других знаков. *Пример: 9686780217*|
|5|date|TEXT|YYYY.MM.DD HH:MM:SS |
|6|places|TEXT|всегда NULL, планировалось - список с ближайшими ВУЗами|
|7|pics|TEXT|список ссылок на фото |
|8|contacts|TEXT| {'phone': <телефон с другими знаками *(например: +7-(968)678-02-17)*>, 'vk': <ссылка на вк>}|
|9|descr|TEXT|Описание объявления|
|10|adr|TEXT|Адрес|
|11|metro|TEXT|Список станций метро|
|12|prooflink|TEXT|URL оъявления|
|13|loc|TEXT| Формат: "lo.ngitude,la.titude"|
|14|fromwhere|TEXT| Атрибут .name того объекта Parse, который внёс эту запись|

#### Таблица Snimu  
Объявления типа **"сниму"**

|ind|Столбец|Тип данных|Комментарии|
|-----|----|----|--------|
|0|hash|TEXT|См [хэширование](hash) |
|1|cost|INTEGER| |
|2|room_num|INTEGER|0 - комната, -1 - койко-место (experimental)|
|3|metro|TEXT|Список станций метро|
|4|phone|TEXT|Код+телефон без других знаков. *Пример: 9686780217*|
|5|contacts|TEXT| {'phone': <телефон с другими знаками *(например: +7-(968)678-02-17)*>, 'vk': <ссылка на вк>}|
|6|prooflink|TEXT|URL оъявления|
|7|pics|TEXT|список ссылок на фото |
|8|descr|TEXT|Описание объявления|

#### Таблица Statuses

|ind|Столбец|Тип данных|Комментарии|
|-----|----|----|--------|
|0|name|TEXT|название парсера|
|1|status|TEXT|см [статусы](#Statuses)

#### Таблица alerts

Хранит json для уведомлений от разработчика.

#### ОБРАЩЕНИЕ К ДАННЫМ БД (!)

sqlite3 возвращает результаты [.fetch](#fetch_db) в виде кортежа, таким образом, обращаться к данным нужно **по индексам (ind в таблицах)**:

```python
# db connection
db = DataBase('parseRes.db')

# get first 20 flats from Results
cmnd = "SELECT * FROM Results LIMIT 20;"
flats = db.fetch(cmnd)

# print every flat's cost and description
for flat in flats:
    cost = flat[1]    # in Results table cost has index=1
    descr = flat[9]   # in Results table descr has index=9
    print(cost, descr)


# get first 20 clients from Snimu
cmnd = "SELECT * FROM Results LIMIT 20;"
flats = db.fetch(cmnd)

# print every client's cost and description
for client in clients:
    cost = client[1]    # in Snimu table cost has index=1
    descr = client[8]   # in Snimu table descr has index=8
    print(cost, descr)

```

<br><br>

<a name="run_it"></a>
## Порядок запуска сервера
<br>
1. Хероку запускает app.py   <br>
2. БД загружается с Dropbox (parser_class.py, line 13)  <br>
3. Проверяем, не пустая ли БД. Если пустая - создаём таблицы (parser_class.py, line 19)  <br>
4. Создаём переменную **DBcon** - глобальный db connection (database.py, line 85)  <br>
5. Cоздаём [**alertBot**](#alertBot) (botAPI.py, line 21)  <br>
6.    Cоздаём PARSER_LIST (из parser_list.json) (app.py, line 29)<br>
7. Запускаем Bottle

<br><br>
## Порядок запуска парсеров
<br>
1. GET на /start_parse<br>
2.    Для каждого парсера из parser_list вызов [parse_it()](#parseit) в отдельном потоке<br>
3. Редирект на "/"