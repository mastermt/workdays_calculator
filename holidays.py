import datetime
import pathlib
import sqlite3
from typing import List, Any, Iterator

import numpy as np
import holidays_database


def sql_execute(sql: str, params: tuple = ()) -> Iterator[Any]:
    con = sqlite3.connect("feriados.db")
    cur = con.cursor()
    res = cur.execute(sql, params)
    if 'UPDATE' in sql.upper():
        con.commit()
    else:
        fetched = res.fetchall()
        con.commit()
        con.rollback()
        return fetched
    con.close()
    return res


def holidays() -> List:
    _holidays = []
    try:
        res = sql_execute(
            "SELECT date FROM holidays"
            " ORDER BY date ASC"
        )
        _data_base_holidays = [dia[0] for dia in res]
        _holidays = np.array(_data_base_holidays, dtype='datetime64')
    except sqlite3.OperationalError:
        holidays_database.cria_tabela()
        # showerror(title='Error', message="Recriando base de dados de feriados")
    return _holidays


def holidays_insert(date_holiday: str) -> bool:
    return_value = False
    try:
        res = sql_execute(
            "INSERT OR IGNORE INTO holidays "
            "(date, description, city, state) "
            "VALUES(?, ?, ?, ?)",
            (date_holiday, '', '', '')
        )
        return True if res else False
    except sqlite3.OperationalError:
        pass
    return return_value


def holidays_delete(date_holiday: str) -> bool:
    return_value = False
    try:
        res = sql_execute(
            "DELETE FROM holidays "
            "WHERE date = ?",
            (date_holiday,)
        )
        return_value = False if res else True
    except sqlite3.OperationalError:
        return_value = False
    return return_value


def work_days(end_day: datetime, days: int) -> int:
    end_day = end_day + datetime.timedelta(days=1)
    start_day = end_day - datetime.timedelta(days=days-1)
    print(f'{start_day} - {end_day}')

    business_days = np.busday_count(
        start_day.date(),
        end_day.date(),
        weekmask='1111100',
        holidays=holidays(),
    )

    return business_days


def backward_work_days(end_day: datetime, days: int) -> np.datetime64:
    # end_day = end_day + datetime.timedelta(days=1)
    business_days = np.busday_offset(
        end_day.date(),
        days,
        roll='backward',
        weekmask='1111100',
        holidays=holidays(),
    )

    return business_days

