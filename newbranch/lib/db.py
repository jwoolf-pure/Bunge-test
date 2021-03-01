import sqlite3

sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS volumes (
                                        id integer PRIMARY KEY,
                                        array text NOT NULL,
                                        volume text,
                                        total text,
                                        snapshots text,
                                        size text,
                                        date text
                                    ); """


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def volume_insert(conn, array, name, total, size, snapshots, date):
    vars = (array,name,total,snapshots,size,date)
    sql = "INSERT INTO volumes(array, volume, total, snapshots, size, date) VALUES(?,?,?,?,?,?)"
    c = conn.cursor()
    c.execute(sql, vars)
    #except:
    #    pass


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)