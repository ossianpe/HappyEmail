import sqlite3 as lite

class Database:
    def __init__(self):
        self.con = None
        self.table_name = ""
    def connect(self, database):
        #Add creating table and insert sample entree into database if does not exist
        self.con = lite.connect(database)
    def disconnect(self):
        self.con.close()
    def set_selected_table(self, tabl_nam):
        self.table_name = tabl_nam
    def get_selected_table(self):
        return self.table_name
    def create_table(self, table_contents):
        #Usage i.e. sqldb.create_table('Address TEXT, Name TEXT, Subscribed TEXT')
        cur = self.con.cursor()
        cur.execute("CREATE TABLE " + self.table_name + "(" + table_contents + ");")
    def add_address_to_table(self, email_addr, nam, subscription_stat):
        #Usage i.e. sqldb.add_address_to_table('jojo@yahoo.com', 'Bob', 'Yes')
        cur = self.con.cursor()
        cur.execute("INSERT INTO " + self.table_name + " VALUES('" + email_addr + "','" + nam + "','" +
            subscription_stat + "');")
        self.con.commit()
        print "Added " + nam + " with email " + email_addr + " to database."
    def remove_address_from_table(self, email_addr):
        cur = self.con.cursor()
        cur.execute("DELETE FROM " + self.table_name + " WHERE Address=\"" + email_addr + "\"")
    def find_column(self, email_addr):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM " + self.table_name + " WHERE Address=\"" + email_addr + "\"")
        return cur.fetchone()
    def change_subscription_status(self, email_addr, subscription_stat):
        #Usage i.e. sqldb.change_subscription_status('jojo@yahoo.com', 'Yes')
        cur = self.con.cursor()
        cur.execute("UPDATE " + self.table_name + " SET Subscribed='" + subscription_stat + "' WHERE Address='" + email_addr + "';")
    def retrieve_data(self):
        with self.con:
            self.con.row_factory = lite.Row
            cur = self.con.cursor()
            cur.execute("SELECT * FROM " + self.table_name)
            rows = cur.fetchall()
            return rows
    def get_length_of_table(self):
        cur = self.con.cursor()
        cur.execute("SELECT count(*) FROM " + self.table_name)
        return cur.fetchone()
    def print_table(self):
        self.con.row_factory = lite.Row
        cur = self.con.cursor()
        cur.execute("SELECT * FROM " + self.table_name)
        rows = cur.fetchall()
        for row in rows:
            print row