from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Executes an SQL file.'

    def handle(self, *args, **options):
        # Get the default SQLite database connection
        connection = connections['default']

        # Specify the path to your SQL file
        sql_file_path = 'sql/createTable.sql'

        # Read the contents of the SQL file
        with open(sql_file_path, 'r') as f:
            sql = f.read()

        # Execute the SQL commands
        with connection.cursor() as cursor:
            cursor. executescript(sql)

        self.stdout.write(self.style.SUCCESS('SQL file executed successfully.'))