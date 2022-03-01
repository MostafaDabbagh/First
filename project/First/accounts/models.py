from django.db import models
from django.db.models.signals import post_save
from ipware import get_client_ip
from django.db import connection


class History(models.Model):
    user_id = models.IntegerField()
    ip = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)

    def add(self, request):
        user_id = request.user.id
        ip = get_client_ip(request)[0]
        browser = request.user_agent.browser.family
        insert_query = "INSERT INTO accounts_history (user_id, ip, browser) " \
                       f"VALUES ({user_id}, '{ip}', '{browser}')"
        select_query = f"SELECT id FROM accounts_history ORDER BY id DESC LIMIT 1"
        with connection.cursor() as cursor:
            cursor.execute(insert_query)
            cursor.execute(select_query)
            history_id = cursor.fetchone()[0]
        self.id, self.user_id, self.ip, self.browser = history_id, user_id, ip, browser
        post_save.send(self.__class__, instance=self, created=True)

