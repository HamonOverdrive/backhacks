import MySQLdb
# hint how to create python anywhere connection code with mysql https://www.pythonanywhere.com/forums/topic/11305/
def connection():
    conn = MySQLdb.connect(host="robautomata.mysql.pythonanywhere-services.com",
                           user = "robautomata",
                           passwd = "niermankind6o",
                           db = "robautomata$myflaskapp"
                           )
    c = conn.cursor()

    return c, conn