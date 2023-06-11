from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Displays SQLite tables in the database.'

    def handle(self, *args, **options):
        table_names = connection.introspection.table_names()

        if table_names:
            self.stdout.write('Tables in the SQLite database:')
            for table_name in table_names:
                self.stdout.write('- ' + table_name)
        else:
            self.stdout.write('The SQLite database does not contain any tables.')