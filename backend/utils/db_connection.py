import mysql.connector

def getDBConnection():
    connection = mysql.connector.connect(
        host = "localhost",
        port = 3306,
        user = "root",
        password ="root",
        database= "smartscheme",
        use_pure=True
    )

    return connection

def executeQuery(sql, params):
    with getDBConnection() as con:
        with con.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            if cur.description:
                return cur.fetchall()
            else:
                con.commit()
                return {
                    "affectedRows": cur.rowcount
                }