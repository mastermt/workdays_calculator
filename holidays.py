import datetime
import pathlib
import sqlite3
from typing import List, Any, Iterator

import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import holidays_database

DATE_FORMAT = '%d/%m/%Y'


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


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.start_day = datetime.datetime.now()
        self.start_date = tk.StringVar()
        self.calculated_days = tk.StringVar()
        self.work_days_label = None
        self.result_label = None
        self.convert_button = None
        self.days_to_calc_entry = None
        self.days_to_calc_label = None
        self.start_date_entry = None
        self.start_date_label = None
        self.space_label = None

        local_path = pathlib.Path(__file__).parent
        icon_png = pathlib.Path(local_path, 'assets', 'images', 'schedule.png')
        self.iconphoto(False, tk.PhotoImage(file=icon_png))

        window_width = 600
        window_height = 300

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        # not resizable
        # self.resizable(False, False)
        # on top
        # self.attributes('-topmost', 1)

        self.title('Calculadora de Dias Úteis')

        # create widget
        self.create_widgets()

    def calcular_dias_button_clicked(self):
        """  Handle calcular_dias button click event
        """
        try:
            end_date = datetime.datetime.strptime(self.start_date.get(), DATE_FORMAT)
            end_date_str = end_date.strftime(DATE_FORMAT)
            calculated_day = int(self.calculated_days.get()) - 1
            if calculated_day < 0:
                showerror(title='Erro', message="Dias tem que ser maior ou igual a 1")
                self.calculated_days.set('1')
                calculated_day = 0
            start_date = (end_date - datetime.timedelta(days=calculated_day)).strftime(DATE_FORMAT)
            days = work_days(end_date, calculated_day) + 1
            result = f'Dias úteis de {start_date} até {end_date_str}: {days}'
            self.result_label.config(text=result)
            date_backward = backward_work_days(end_date, calculated_day * (-1))
            result = f'{calculated_day + 1} úteis antes de {end_date_str}: {date_backward.item().strftime(DATE_FORMAT)}'
            self.work_days_label.config(text=result)
        except ValueError as error:
            showerror(title='Erro', message=str(error))

    def keypad_chance_value(self, value, event):
        try:
            calculated_day = int(self.calculated_days.get()) + value
            self.calculated_days.set(str(calculated_day))
        except ValueError as error:
            showerror(title='Erro', message=str(error))
            self.calculated_days.set('1')

    def on_key_release_kp_add(self, event):
        # Check to see if string consists of only integers
        if not event.char.isdigit():
            self.calculated_days.set(self.calculated_days.get().removesuffix('+').removesuffix('-'))

    def create_widgets(self):
        # padding for widgets using the grid layout
        paddings = {'padx': 10, 'pady': 10}

        # spacing label
        self.space_label = ttk.Label(self, text='')
        self.space_label.grid(column=0, row=1, sticky='W', **paddings)

        # start_date label
        self.start_date_label = ttk.Label(self, text='Data final:')
        self.start_date_label.grid(column=0, row=3, sticky='W', **paddings)

        # start_date entry
        self.start_date_entry = ttk.Entry(self, textvariable=self.start_date)
        self.start_date_entry.grid(column=1, row=3, **paddings)
        self.start_date_entry.insert(0, datetime.datetime.strftime(datetime.datetime.now(), DATE_FORMAT))
        self.start_date_entry.focus()

        # days_to_calc label
        self.days_to_calc_label = ttk.Label(self, text='Dias a calcular:')
        self.days_to_calc_label.grid(column=0, row=4, sticky='W', **paddings)

        # days_to_calc entry
        self.days_to_calc_entry = ttk.Entry(self, textvariable=self.calculated_days)
        self.days_to_calc_entry.grid(column=1, row=4, **paddings)
        self.days_to_calc_entry.bind('<Return>', lambda event: self.calcular_dias_button_clicked())
        self.days_to_calc_entry.bind('<KP_Enter>', lambda event: self.calcular_dias_button_clicked())
        self.days_to_calc_entry.bind('<KP_Add>', lambda event: self.keypad_chance_value(1, event))
        self.days_to_calc_entry.bind('<KP_Subtract>', lambda event: self.keypad_chance_value(-1, event))
        self.days_to_calc_entry.bind('<Next>', lambda event: self.keypad_chance_value(-10, event))
        self.days_to_calc_entry.bind('<Prior>', lambda event: self.keypad_chance_value(10, event))
        self.days_to_calc_entry.bind("<KeyRelease>", self.on_key_release_kp_add)
        self.days_to_calc_entry.focus()

        # convert button
        self.convert_button = ttk.Button(self, text='Calcular')
        self.convert_button.grid(column=2, row=4, sticky='W', **paddings)
        self.convert_button.configure(command=self.calcular_dias_button_clicked)

        # result label
        self.result_label = ttk.Label(self, foreground='red', font=('Arial', 14, 'bold'))
        self.result_label.grid(row=5, columnspan=3, **paddings)

        # result2 label
        self.work_days_label = ttk.Label(self, foreground='blue', font=('Arial', 14, 'bold'))
        self.work_days_label.grid(row=6, columnspan=3, **paddings)


if __name__ == "__main__":
    app = App()
    app.mainloop()
