# hoROOMy parsers system

## Содержание


## Структура

### Root
<br><br><br><br>
##### .py файлы  

*app.py* -- сервер на Bottle  
*botAPI.py* -- телеграм-бот (for alerts)  
*database.py* -- методы работы с базой данных  
*driveAPI.py* -- методы Dropbox - костыль  
*parseAPI.py* -- **парсеры тут**  
*parser_class.py* -- определение класса **Parse** для оптимизации

##### Файлы для сервера  

*.gitignore*  
*procfile*  
*requirements.txt* -- используемые библиотеки  
*runtime.txt* -- версия интерпретатора

##### Прочие файлы  

*parseRes.db* -- база данных сервера  
*parser_list.json* -- список активных парсеров

### html

##### Системные  

*main.html* -- управление парсерами*//  
*main-adm.html* -- редактировать main//  

##### Для пользователя

*search.html* -- поиск по базе  
*tableRes.html* -- результаты поиска*//  
*circler.html* -- показать дом на карте*  

##### Сырое  

*metroLookAround.html* -- выводит соседние станции метро по данной (in production)*  
*stats.html* -- форма получения статистики из БД (unnecessary)  
*giveMeStats.html* -- статистика по параметрам из формы//  
```
* -- includes JS code  
// -- is rendered as a template  
```

### css  

*style.css* -- стили для *tableRes.html*

### pics  

*foto.png* -- если фотографии в объявлении отсутствуют (для *tableRes.html*)

## Методы сервера  

Обращения к серверу осуществляются с помощью GET-запросов. **POST запросы не используются в данном АПИ.**

### System  

Консоль администратора

#### /system/  

Графический интерфейс управления парсерами. Требует ввода логина и пароля.
>Отуствует хэширование и хранение пар **логин-хэш** в базе данных. Данная функция создана только для защиты от "дураков".

Авторизация через Auth headers.

#### /system/edit  

HTML страница для редактирования блока *"Уведомления от разработчика"* в main.html -- ~~ненужная фигня~~ 

#### /system/сhangemain  

HTML из `/system/edit` посылает GET-запрос сюда для изменения блока *"Уведомления от разработчика"*  
~~Не задокументировано, так как нафиг никому не нужно~~

### Parsers  

Методы управления парсерами

#### /parsers/start_social  

Начать парсинг записей ВК  
**Необязательные параметры**:
* num=<int> - количество записей, которые необходимо взять у каждой группы (по умолчанию 100)

#### /parsers/start_parse  

Запустить все парсеры агрегаторов (то есть всё, кроме парсинга ВК)
**Необязательные параметры**:
* maxprice=<int> - ограничение по цене для квартир (по умолчанию 55000)

#### /parsers/special_parse  

Тестирование одного парсера:
* Для ВК: парсинг 100 записей в каждой группе
* Для других парсеров: парсинг объявлений с maxprice=15000

***Обязательные*** **параметры**:

* parser_name=<str> -- парсер, который надо протестировать

>**Значения parser_name:**
?parser_name=***vk*** -- парсинг вк
?parser_name=***<название парсера из parser_list.json>*** - запуск данного парсера


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

### Results

#### /results/giveMeResults/<parser_name>  

Возвращает [json с данными](resultsFormat), полученными указанным парсером.  
*Версия с большим количеством параметров --* [/giveMeFlats](giveMeFlats)

#### /results/clearAll  

Очищает таблицы Results и Snimu в [базе данных](databaseStructure).

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

### Statuses  

Методы проверки состояния парсеров
*****
***Cтатус может принимать следующие значения:***
* *натуральное число* -- парсер ещё не завершил работу, возвращается кол-во обработанных страниц/объявлений (зависит от парсера)
* *last updated on: YYYY.MM.DD HH:MM:SS*
* *last updated on: never* -- в бд нет данных этого парсера
*****

#### /statuses/plist  

Возвращает список активных парсеров *(parser_list.json)*

#### /statuses/giveMeStatus/<parser>  

Возвращает статус для данного парсера.

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

### User Experience  

#### /search  

Возвращает search.html

#### /giveMeFlats  

Возвращает список из 20 объектов (квартиры, комнаты) по данным параметрам

**Необязательные параметры:**
* dealType -- тип объекта
>Значения dealType:
***Flat*** -- квартира
***Room*** -- комната
**По умолчанию:** dealType=Room
* metro -- станция метро (не указано => возвращаются кв. в районе любого метро)
>Значения metro: название любой станции метро Москвы
**Список всех значений приведён в search.html**
* room_num -- комнатность (не указано => любая)
>Значения room_num:
***n*** - n-комнатная квартира (n от 1 до 3)
* cost -- ориентировочная цена, руб (не указано => любая)
* page -- страница (по умолчанию - 1)
* html -- формат вывода данных
Значения html:
>***off*** -- вывод json-списка
***on*** -- возврат обработанного шаблона tableRes.html
***count*** -- возврат кол-ва результатов поиска

**По умолчанию: html=on**

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

### Map  

#### /map/geolocate  

Возвращает circler.html с указанием места на карте

***Обязательные*** **параметры**:
* loc - строка типа "<lo.ngitude>,<la.titude>"

Если не указан парметр loc, возникает **Error 500**

### DataBase

#### /db/download  

Загрузка базы данных на устройство

#### /db/sync  

[Выгрузка базы данных в dropbox](dropbox)

### Stuff  

#### /pics/<filename>  

Получить картирку по названию из каталога ./pics/

#### /css/<filename>  

Получить stylesheet по названию из каталога ./css/

## Классы  

### DataBase (database.py)  

```python
class DataBase:
    name = ''
    _db_connection = None
    _db_cur = None
```
#### .query(self, query)  

Executes a single SQL statement.  

#### .fetch(self, query)  

Returns the result of a statement execution.  

#### .format(self)  

Create [all tables]('db_tables')  

#### .delete_table(self, table)  

Clear all results in a table  

#### `__del__`(self)  

Close DataBase connection.  

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

### BackuppedFile (driveAPI.py)  

Все изменения в файлах, хранящихся на heroku, сбрасываются при перезагрузке сервера (перезагрузка осуществляется автоматически не менее одного раза в день).
Чтобы сохранять и восстанавливать эти изменения, введён класс BackuppedFile.
```python
class BackuppedFile:
    filename = ''       # filename on the device
    DBXfilename = ''    # filename in the cloud
```
#### .upload(self)  

Выгрузить файл в Dropbox - сохранить изменения.  

#### . sync(self)  

Загрузить файл с Dropbox на устройство - восстановить изменения.  

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

### Parse (parser_class.py)  

```python
class Parse:
    name = ""
    db = None   # each parser has its own db connection to enable multithreading
```
#### .write_status(self, status=<int>)  

Вносит новый статус (количество обработанных объявлений) в таблицу `Statuses` бд для данного парсера (self.name).  

#### .add_date(self)  

Пишет `last updated on: YYYY.MM.DD HH:MM:SS` в таблицу `Statuses` бд.  

#### .get_results(self)  

Возвращает результаты, полученные этим парсером  

#### .get_status(self)  

Возвращает статус данного парсера  

#### .append(self, data, useHash=False)  

Добавляет данные из словаря `data` в таблицу `Results`.  

```python
if useHash:
    unique_id = hash(data['descr'])
else:
    unique_id = getUID(data)
```
#### .append_snimu(self, data)  

Добавляет данные из `data` в таблицу `Snimu`.
**Всегда используется hash() для получения идентификатора объявления**  

#### `__del__`(self)  

Закрывает соединение с `self.db`.  

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