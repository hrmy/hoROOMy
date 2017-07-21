# **hoROOMy**   Vk posts API
*****

>Если лень читать всё это
>[Внизу](#shortcuts) есть shortcuts


## Запрос

#### URL запроса:
https://horoomy-parsers.herokuapp.com/giveMePosts/<params>

#### Параметры:
##### URL
*/sdam* -- объявления из категории сдам (скорее всего)
*/snimu* -- объявления из категории сниму
##### GET-Request query (необязательные параметры)
*?num=<int>* -- количество постов

## Ответ

#### Type

*Тип ответа* -- JSON-строка
*Формат*:
```
[[post0], [post1], [post2], ...]
```

#### Приоритетность:
Текст описания может начинаться cтрокой `----!PRIORITY!----`. Это значит, что в посте есть фразы, которые были указаны нам как приоритетные (*сниму покомнатно, сдам квартиру* и другие).

## Примеры

```
r = requests.get("https://horoomy-parsers.herokuapp.com/giveMePosts/sdam?num=100")
posts = json.loads(r.text)

print(len(posts), "elements in the list")   # 100 elements in the list

for post in posts:
    print(post[0])    # print all posts' text
    
#----------------------------------------------------------------------

r = requests.get("https://horoomy-parsers.herokuapp.com/giveMePosts/snimu")
many_posts = json.loads(r.text)

print(len(many_posts), "elements in the list")  # over9000 elements in the list
```

<a name="shortcuts"></a>
## Shortcuts

##### Получить 150 записей *сдам*:
https://horoomy-parsers.herokuapp.com/giveMePosts/sdam?num=150

##### Получить 150 записей *сниму*:
https://horoomy-parsers.herokuapp.com/giveMePosts/snimu?num=150