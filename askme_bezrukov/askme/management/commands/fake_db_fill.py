from django.core.management.base import BaseCommand, CommandParser
from askme.models import Profile, Question, Answer, Tag, User, UsersLikes
from random import choice, sample, randrange
from faker import Faker

faker = Faker()

class Command(BaseCommand):
    help = 'fill db with fake data'


    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--ratio', '-r', type=int)


    def fill_tags(self, amount):
        for i in range(amount):
            title = faker.word()
            print ("try")
            while (not Tag.objects.check_tag(title)):
                #print (title)
                title = faker.word() + ' ' + str(randrange(100))
            print ("uspeh")
            Tag.objects.create(title = title, usage_amount = 0)


    def fill_profiles(self, amount):
        for i in range (amount):
            uname = faker.user_name()
            email = faker.email()

            while (not Profile.objects.check_user(uname, email)):
                print('retry')
                uname = faker.user_name()
                email = faker.email()

            user = User.objects.create_user(uname, email, faker.password())

            user.save()
            Profile.objects.create(rating=faker.random_int(min=-50, max=1000), avatar = '/static/img/ava.png', user=user)


    def fill_questions(self, amount):
        profiles_id = list (Profile.objects.values_list('id', flat=True))
        tags_id = list(Tag.objects.values_list('id', flat=True))
        for i in range (amount):
            question = Question.objects.create(
                title = faker.sentences(faker.random_int(min=1, max=3)),
                text = faker.sentences(faker.random_int(min=5, max=10)),
                rating = 0,
                ask_datetime = faker.date_time(),
                answers_amount = 0,
                author = Profile.objects.get(pk=choice(profiles_id))    
            )
            question.save()

            question_taglist = sample(tags_id, faker.random_int(min=1,max=5))
            for question_tag in question_taglist:
                tag = Tag.objects.get(pk=question_tag)
                tag.usage_amount += 1
                tag.save()
                question.tags.add(tag) 
                
            question.save()


    def fill_answers(self, amount):
        profiles_id =  list(Profile.objects.values_list('id', flat=True))
        questions_id = list(Question.objects.values_list('id', flat=True))
        for i in range (amount):
            question = Question.objects.get(pk=choice(questions_id))
            question.answers_amount += 1
            question.save()
            answer = Answer.objects.create(
                text = faker.sentences(faker.random_int(min=5, max=10)),
                is_verified = choice([True,False]),
                rating = 0,
                answ_datetime = faker.date_time(),
                question = question,
                author = Profile.objects.get(pk=choice(profiles_id))
            )
            answer.save()


    def fill_ratings(self, amount):
        questions_id = list(Question.objects.values_list('id', flat=True))
        answers_id = list(Answer.objects.values_list('id', flat=True))
        profiles_id =  list(Profile.objects.values_list('id', flat=True))
        for i in range (amount):
            rating_object = choice([Question.objects.get(pk=choice(questions_id)), Answer.objects.get(pk=choice(answers_id))])
            profile = Profile.objects.get(pk=choice(profiles_id))
            while (not UsersLikes.objects.rating_exists(profile, rating_object.id)):
                profile = Profile.objects.get(pk=choice(profiles_id))
            rate = choice([-1,1])
            rating_object.rating += rate     
            rating_object.save()
            profile.rating += rate
            profile.save()
            UserLike = UsersLikes.objects.create(
                user = profile,
                rate = rate,
                content_object = rating_object
            )
            UserLike.save()
            

    def handle(self, *args, **options):
        ratio = options['ratio']
        if (ratio<10001):
            raise ValueError("not enough ratio")
        self.fill_profiles(ratio)
        self.fill_tags(ratio)
        self.fill_questions(10*ratio)
        self.fill_answers(100*ratio)
        self.fill_ratings(200*ratio)        

