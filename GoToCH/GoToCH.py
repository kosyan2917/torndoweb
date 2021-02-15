import tornado.ioloop
import tornado.web
import json
from bson import ObjectId
import uuid
from pymongo import MongoClient

'''
1. главная страница - список тредов - MainHandler - GET - /
2. добавление треда - MainHandler - POST - /
3. список постов в треде - ThreadHandler - GET - /thread?id=THREAD_ID
4. добавление поста в тред - ThreadHandler - POST - /thread?id=THREAD_ID
[
    {"name": "мемы", "posts": [
            {"author": "Аноним", "text": "текст поста"}
        ]
    },
    {"name": "мемы", "posts": [
            {"author": "Аноним", "text": "текст поста"}
        ]
    }
]
'''

# создать конекшн к монге
connection = MongoClient("mongodb://nik:admin@ds119548.mlab.com:19548/gotoch")

# выбрать бд
database = connection['gotoch']

# выбрать коллекцию
threads_collection = database['threads']

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # выдача страницы с тредами
        threads = list(threads_collection.find())
        #print(threads)

        self.render("threads.html", threads=threads)
    def post(self):
        # добавление поста
        name = self.get_argument("name")
        thread = {"name": name, "posts": []}

        threads_collection.insert(thread)

        self.redirect('/')



class ThreadHandler(tornado.web.RequestHandler):
    def get(self):
        thread = threads_collection.find_one({'_id': ObjectId(self.get_argument('id'))})
        id = thread['_id']
        thread_name = thread['name']
        posts = thread['posts']
        # выдача страницы с постами
        # TODO: Написать шаблон для страницы с постами (похожий на главную страницу)
        # TODO: Взять тред из монги, у которого {'_id': ObjectId(self.get_argument('id'))}

        # TODO: Зарендерить шаблон с постами этого треда
        self.render("posts.html", posts=posts, thread=thread_name, id=id )

    def post(self):
        # добавление поста
        auth = self.get_argument('name', '')
        text = self.get_argument('post', '')
        thread = threads_collection.find_one({'_id': ObjectId(self.get_argument('id'))})
        if text != '':
            if auth == '':
                posts = thread['posts']
                posts.append({'id': str(uuid.uuid4()),'auth': "Anonymus", "text": text, 'like': 0, 'comment': []})
                threads_collection.update({'_id': ObjectId(self.get_argument('id'))}, thread)
            else:
                posts = thread['posts']
                posts.append({'id': str(uuid.uuid4()),'auth': auth, "text": text, 'like': 0, 'comment': []})
                threads_collection.update({'_id': ObjectId(self.get_argument('id'))}, thread)

        self.redirect('/thread?id={0}'.format(str(thread['_id'])))

        # TODO: Получить параметры из запроса (self.get_argument...)
        # TODO: сделать новый пост
        # TODO: добавить пост в тред и сохранить в монге
        # TODO: редирект на страницу с постами
class LikeHandler(tornado.web.RequestHandler):
    def get(self):
        thread_id = self.get_argument('thread')
        print(str(thread_id))
        post_id = self.get_argument('id')
        print(post_id)
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)})
        print(thread)
        posts = thread['posts']
        for post in posts:
            print(1)
            if post['id']==post_id:
                print(2)
                post['like'] += 1
        threads_collection.update({'_id': ObjectId(thread_id)}, thread)
        self.redirect("/thread?id={0}".format(thread_id   ))
class CommentHandler(tornado.web.RequestHandler):
    def post(self):
        thread_id = self.get_argument('thread')
        post_id = self.get_argument('id')
        thread = threads_collection.find_one({'_id': ObjectId(thread_id)})
        posts = thread['posts']
        name = self.get_argument('name', '')
        comment = self.get_argument('comment')
        for post in posts:
            if post['id']==post_id:
                comments = post['comment']
                break
        if name!="":
            comments.append({'name': name, "text": comment})
            threads_collection.update({'_id': ObjectId(thread_id)}, thread)
        else:
            comments.append({'name': 'Anonymus', "text": comment})
            threads_collection.update({'_id': ObjectId(thread_id)}, thread)
        self.redirect("/thread?id={0}".format(thread_id))
routes = [
    (r"/", MainHandler),
    (r"/thread", ThreadHandler),
    (r"/thread/like", LikeHandler),
    (r'/thread/comment', CommentHandler)
]

app = tornado.web.Application(routes, debug=True)
app.listen(8888)
tornado.ioloop.IOLoop.current().start()