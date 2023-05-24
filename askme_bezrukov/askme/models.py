from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ProfileManager(models.Manager):
    def get_users_top(self):
        return self.order_by('-rating')[:5]
    
    def check_user(self, name, email):
        uamount = User.objects.filter(username = name).count()
        if uamount == 0: 
            return False
        return True


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT)
    rating = models.IntegerField(default=0)
    avatar = models.ImageField(default='avatars/default/ava.png', upload_to='avatars/%Y/%m/%d/')
    objects = ProfileManager()


class TagManager(models.Manager):
    def get_top_tags(self):
        return self.order_by('-usage_amount')[:10]

    def check_tag(self, title):
        tamount = Tag.objects.filter(title = title).count()
        if tamount == 0: 
            return False
        return True 
        
    def create_with_list(self, tags):
        for tag in tags:
            if not self.check_tag(tag):
                self.create(title=tag)
    

class Tag(models.Model):
    title = models.CharField(max_length=20, unique=True)
    usage_amount = models.PositiveIntegerField(default=0)
    objects = TagManager()


class QuestionManager (models.Manager):
    def get_newest(self):
        return self.filter(solved = False).order_by('-ask_datetime')

    def get_hottest(self):
        return self.filter(solved = False).order_by('-rating')

    def get_by_tag(self, tag):
        return self.filter(solved = False, tags__title__icontains=tag).order_by('-rating')  



class Question (models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=10000)
    author = models.ForeignKey(Profile, on_delete=models.RESTRICT, null=True)
    ask_datetime = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True)
    answers_amount = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)

    objects = QuestionManager()

    def add_tags(self, tags):
        for tag in tags:
            self.tags.add(Tag.objects.filter(title=tag)[0])    


class AnswerManager(models.Manager):
    def newest(self, question_id):
        question = Question.objects.get(pk=question_id)
        return self.filter(question=question).order_by('-ask_datetime')

    def hottest(self, question_id):
        question = Question.objects.get(pk=question_id)
        return self.filter(question=question).order_by('-rating')  

    def verify_answer(self, answer_id, is_right):
        answer = self.get(pk=answer_id)
        answer.is_verified = is_right
        return answer.save()       


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(max_length=5000)
    author = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    answ_datetime = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default = False)
    rating = models.IntegerField(default=0)
    objects = AnswerManager()


class UsersLikesManager(models.Manager):
    def rating_exists(self, user_id, object_id):
        ramount = UsersLikes.objects.filter(user_id = user_id, object_id = object_id).count()
        if ramount == 0: 
            return False
        return True
    
    def rate_object(self, user, object, rate):
        object.author.rating += rate
        object.rating += rate
        object.author.save()
        object.save()
        self.create(user = user.profile, rate=rate, content_object = object)
        return object.author.rating, object.rating



class UsersLikes(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    rate = models.SmallIntegerField(choices=((-1, 'DIS'), (1, 'LIKE')))

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = UsersLikesManager()
