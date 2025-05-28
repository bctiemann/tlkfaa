from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from fanart.utils import dictfetchall


class Command(BaseCommand):

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            query = """
                show tables
            """
            cursor.execute(query, [])
            result = cursor.fetchall()
            for r in result:
                table = r[0]
                print(table)
                query = f"""
                    show indexes from {table}
                """
                cursor.execute(query, [])
                indexes = dictfetchall(cursor)
                for i in indexes:
                    print(f"{i['Cardinality']}\t{i['Key_name']}")
                cardinalities = [i['Cardinality'] for i in indexes]
                if all([c in [0, 1] for c in cardinalities]):
                    print('needs analyze')
                    query = f"""
                       analyze table {table}
                    """
                    cursor.execute(query, [])
