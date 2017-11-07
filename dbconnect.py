
import MySQLdb.cursors
# hint how to create python anywhere connection code with mysql https://www.pythonanywhere.com/forums/topic/11305/
def connection():
    conn = MySQLdb.connect(host="robautomata.mysql.pythonanywhere-services.com",
                           user = "robautomata",
                           passwd = "niermankind6o",
                           db = "robautomata$myflaskapp", cursorclass=MySQLdb.cursors.DictCursor)
    c = conn.cursor()

    return c, conn