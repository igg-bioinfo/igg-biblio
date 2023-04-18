import pandas as pd
from datetime import datetime 

class Demo:
    st = None
    db = None
    id = 0
    name = ""
    user_name = ""
    user_type = ""
    update_date = None
    update_count = None
    update_days = None


    def __init__(self, st, db):
        self.st = st
        self.db = db

    def get_update_details(self):
        self.db.cur.execute('SELECT date_update, count(inv_id) FROM investigators  WHERE date_update = (SELECT MAX(date_update) FROM investigators) GROUP BY date_update')
        res = self.db.cur.fetchall()
        df = pd.DataFrame(res, columns=["update", "id"])
        if len(df) > 0:
            self.update_date = df["update"][0]
            self.update_count = df["id"][0]
            dt = datetime.date(datetime.now()) - self.update_date
            self.update_days = dt.days
            return True
        return False