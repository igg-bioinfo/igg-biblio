import psycopg2
class DB:
    conn = None
    cur = None
    st = None

    def __init__(self, st):
        self.st = st

    def connect(self):
        self.conn = None
        self.cur = None
        with self.st.spinner():
            try:
                self.conn = psycopg2.connect(
                    host = self.st.secrets["db_host"],
                    database = self.st.secrets["db_name"],
                    user = self.st.secrets["db_username"],
                    password = self.st.secrets["db_password"])
                self.cur = self.conn.cursor()
            except (Exception, psycopg2.DatabaseError) as error:
                self.st.write(error)
        if not self.running():
            self.st.error("Connession al database fallita")
            self.st.stop()

    def running(self):
        return self.conn is not None and self.cur is not None
    
    def close(self):
        self.cur.close()
        self.conn.close()