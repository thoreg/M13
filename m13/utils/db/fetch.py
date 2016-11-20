def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict - stolen from django project documentation.

    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row)) for row in cursor.fetchall()
    ]
