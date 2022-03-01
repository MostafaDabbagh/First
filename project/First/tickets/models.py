import os.path

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from First.settings import BASE_DIR
from utils.text_to_image import text_to_image
from django.db import connection
from utils.strings import most_frequent_words


def user_can_ticket(user):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) "
                       "FROM tickets_ticket "
                       "WHERE date_trunc('hour', created) = date_trunc('hour', CURRENT_TIMESTAMP) "
                       f"AND user_id = {user.id}")
        this_hour_tickets = cursor.fetchone()[0]
    if this_hour_tickets < Ticket.TICKET_PER_HOUR_LIMIT:
        return True
    return False


def all_tickets_per_day():
    with connection.cursor() as cursor:
        cursor.execute("SELECT dates.d, COUNT(tickets_ticket.created) "
                       "FROM (SELECT (CURRENT_DATE - i) AS d FROM generate_series(30,1,-1) AS i) dates "
                       "LEFT JOIN tickets_ticket "
                       "ON CAST(tickets_ticket.created AS DATE) = dates.d "
                       "GROUP BY dates.d "
                       "ORDER BY dates.d ASC")
        raw_data = cursor.fetchall()
    chart_data = [[], []]
    for element in raw_data:
        chart_data[0].append(f"{element[0].strftime('%B')[0:3]} {element[0].day}")
        chart_data[1].append(element[1])
    return chart_data


def user_tickets_per_day(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT dates.d, COUNT(tickets_ticket.created) "
                       "FROM (SELECT (CURRENT_DATE - i) AS d FROM generate_series(30,1,-1) AS i) dates "
                       "LEFT JOIN tickets_ticket "
                       f"ON CAST(tickets_ticket.created AS DATE) = dates.d AND user_id = {user_id} "
                       "GROUP BY dates.d "
                       "ORDER BY dates.d ASC")
        raw_data = cursor.fetchall()
    chart_data = [[], []]
    for element in raw_data:
        chart_data[0].append(f"{element[0].strftime('%B')[0:3]} {element[0].day}")
        chart_data[1].append(element[1])
    return chart_data


def chars_per_user():
    with connection.cursor() as cursor:
        cursor.execute("SELECT username, COALESCE(SUM(char_length(text)), 0) "
                       "FROM auth_user "
                       "LEFT JOIN tickets_ticket "
                       "ON auth_user.id = tickets_ticket.user_id "
                       "GROUP BY username "
                       "ORDER BY username")
        raw_data = cursor.fetchall()
    chart_data = {}
    for element in raw_data:
        chart_data[element[0]] = element[1]
    return chart_data


def most_used_words(user_id):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT text FROM tickets_ticket WHERE user_id = {user_id}")
        raw_data = cursor.fetchall()
    text = ''
    for element in raw_data:
        text += element[0] + ' '
    words = most_frequent_words(text)
    return words[0:5]


class Ticket(models.Model):
    TICKET_PER_HOUR_LIMIT = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField()
    ip = models.GenericIPAddressField()
    browser = models.CharField(max_length=50)

    def send_email(self):
        user = self.user
        subject = 'Your ticket has been sent'
        body = f'Thank you {user.username}.We have received your ticket now. We will check it and contact you as soon as possible'
        email_message = EmailMessage(subject, body, 'myfirstproject1400@gmail.com', [user.email])
        image_name = f'ticket-{user.username}-{self.id}.png'
        image_path = os.path.join(BASE_DIR, f'media/ticket_images/{image_name}')
        text_to_image(self.text, image_path)
        email_message.attach_file(image_path)
        email_message.send(fail_silently=False)

    @staticmethod
    def ticket_dict_to_object(td):
        return Ticket(id=td['id'],
                      user_id=td['user_id'],
                      text=td['text'],
                      created=td['created'],
                      ip=td['ip'],
                      browser=td['browser'])

    @staticmethod
    def get(ticket_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets_ticket "
                           f"WHERE id = {ticket_id}")
            columns = [col[0] for col in cursor.description]
            ticket_dict = dict(zip(columns, cursor.fetchone()))
        ticket = Ticket.ticket_dict_to_object(ticket_dict)
        return ticket

    @staticmethod
    def filter(user_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets_ticket "
                           f"WHERE user_id = {user_id}")
            columns = [col[0] for col in cursor.description]
            tickets_dict = [dict(zip(columns, row)) for row in cursor.fetchall()]
        tickets = [Ticket.ticket_dict_to_object(td) for td in tickets_dict]
        return tickets

    @staticmethod
    def get_last_ticket_id():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM tickets_ticket ORDER BY id DESC LIMIT 1")
            last_ticket_id = cursor.fetchone()[0]
        return last_ticket_id

    def insert(self):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO tickets_ticket (user_id, text, created, ip, browser) "
                           f"VALUES ({self.user_id}, '{self.text}', CURRENT_TIMESTAMP, '{self.ip}', '{self.browser}')")
        self.id = self.get_last_ticket_id()

    def update(self):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE tickets_ticket "
                           f"SET text = '{self.text}' "
                           f"WHERE id = {self.id}")

    def remove(self):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tickets_ticket "
                           f"WHERE id = {self.id}")

    def has_file(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets_file "
                           f"WHERE ticket_id = {self.id}")
            data = cursor.fetchone()
            if data:
                return True
            return False


class File(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    filename = models.TextField(max_length=200)

    @staticmethod
    def file_dict_to_object(td):
        return File(id=td['id'],
                    ticket_id=td['ticket_id'],
                    filename=td['filename'])

    @staticmethod
    def get(ticket_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tickets_file "
                           f"WHERE ticket_id = {ticket_id}")
            columns = [col[0] for col in cursor.description]
            file_dict = dict(zip(columns, cursor.fetchone()))
        file = File.file_dict_to_object(file_dict)
        return file

    def insert(self):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO tickets_file (ticket_id, filename) "
                           f"VALUES ({self.ticket_id}, '{self.filename}')")

    def update(self):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE tickets_file "
                           f"SET filename = '{self.filename}' "
                           f"WHERE ticket_id = {self.ticket_id}")

    def remove(self):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tickets_file "
                           f"WHERE ticket_id = {self.ticket_id}")

