#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import calendar
from typing import List, Tuple

# import pathlib
import flet as ft
import holidays

DATE_FORMAT = '%d/%m/%Y'
WEEK_DAYS = ("Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab")
MONTHS = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
    "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
)
calendar.setfirstweekday(calendar.SUNDAY)
_HOLIDAYS = set(holidays.holidays())


def main(page: ft.Page):

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Escape":
            page.close()
        elif e.key in ("Enter", "Return", "Numpad Enter"):
            button_calcular_clicked(e)
            tf_days.focus()
            page.update()

    def get_grid_month_datatable(
            list_mount: List, par_month: int, par_year: int
    ) -> ft.DataTable:
        grip_datatable = ft.DataTable(
            bgcolor="gray",
            # border=ft.border.all(2, "black"),
            border_radius=10,
            divider_thickness=0,
            column_spacing=16,
            heading_row_color=ft.colors.BLACK12,
            heading_row_height=20,
            data_row_height=25,
            columns=[
                ft.DataColumn(
                    ft.Text(day_week),
                    numeric=True,
                ) for day_week in WEEK_DAYS
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                [
                                    get_menu(
                                        day_month=day, day_week=day_week,
                                        year=par_year, par_month=par_month
                                    ) if day else ft.Text(''),
                                ],
                            )
                        ) for day_week, day in enumerate(week)
                    ]
                ) for week in list_mount
            ]
        )
        return grip_datatable

    def get_menu(
            day_month: int = 0,
            day_week: int = 0,
            year: int = 0,
            par_month: int = 0
    ) -> ft.PopupMenuButton:
        global _HOLIDAYS
        color = ft.colors.RED if day_week in (0, 6) else ft.colors.BLUE
        day_now = f"{year}-{par_month:02}-{day_month:02}"
        if day_now in [str(day) for day in _HOLIDAYS]:
            color = ft.colors.RED
        pm_button = ft.PopupMenuButton(
            content=ft.Text(
                str(day_month),
                color=color,
                text_align=ft.TextAlign.CENTER
            ),
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.CALENDAR_TODAY_ROUNDED),
                            ft.Text("Adicionar feriado"),
                        ]
                    ),
                    on_click=lambda _: holidays_insert(day_now),
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.HOURGLASS_TOP_OUTLINED),
                            ft.Text("Remover feriado"),
                        ]
                    ),
                    on_click=lambda _: holidays_delete(day_now),
                ),
            ]
        )
        return pm_button

    def holidays_update_calendar(_final_date: datetime) -> None:
        for control in page.controls:
            if isinstance(control, ft.GridView):
                # print(f'Removendo calendário {_final_date} de {control.uid}')
                page.controls.remove(control)

        calendars = ft.GridView(
            runs_count=3,
            max_extent=440,
            child_aspect_ratio=1.5,
            spacing=5,
            run_spacing=5,
            expand=True,
        )

        month_range_count = int((1 + (int(tf_days.value) / 27.5)) * 1.4505)
        print(f'start day: {tf_final_date.value}')
        print(f'count: {(1 + (int(tf_days.value) / 27.5)) * 1.4405}')
        if sw_reverse.value:
            month_range: Tuple = (
                _final_date.month,
                _final_date.month + month_range_count
            )
        else:
            month_range = (
                _final_date.month - month_range_count + 1,
                _final_date.month + 1
            )
        print(f'range({month_range}), count:{month_range_count}')

        for index_month in range(*month_range):
            cal_month = index_month if index_month > 0 else 12 + index_month
            cal_year = _final_date.year if index_month > 0 else _final_date.year - 1
            if cal_month > 12:
                cal_month = cal_month - 12
                cal_year = cal_year + 1
            # print(
            #     (
            #         f"{index_month} <> {cal_month}, {cal_year}"
            #         f" <> {cal_year}"
            #     )
            # )
            calendars.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"{MONTHS[cal_month - 1]} {cal_year}",
                                        text_align=ft.TextAlign.CENTER,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Container(
                                content=get_grid_month_datatable(
                                    calendar.monthcalendar(cal_year, cal_month),
                                    cal_month, cal_year
                                ),
                                alignment=ft.alignment.center,
                            ),
                        ],
                    ),
                    bgcolor=ft.colors.AMBER_100,
                    alignment=ft.alignment.center,
                    padding=5,
                    border_radius=10,
                )
            )
        page.add(calendars)
        page.update()

    def holidays_insert(day_now: str) -> None:
        global _HOLIDAYS
        holidays.holidays_insert(day_now)
        _HOLIDAYS = set(holidays.holidays())
        button_calcular_clicked(None)
        holidays_update_calendar(
            datetime.datetime.strptime(tf_final_date.value, DATE_FORMAT)
        )

    def holidays_delete(day_now: str) -> None:
        global _HOLIDAYS
        holidays.holidays_delete(day_now)
        _HOLIDAYS = set(holidays.holidays())
        button_calcular_clicked(None)
        holidays_update_calendar(
            datetime.datetime.strptime(tf_final_date.value, DATE_FORMAT)
        )

    page.title = "Calculadora de Dias Úteis"
    icon_image = ft.Image(
        src="/images/schedule.png",
        width=128,
        height=128,
        fit=ft.ImageFit.SCALE_DOWN,
    )

    def button_calcular_clicked(e):
        if e:
            pass
        
        try:
            end_date = datetime.datetime.strptime(tf_final_date.value, "%d%m%Y")
        except ValueError:
            try:
                end_date = datetime.datetime.strptime(tf_final_date.value, DATE_FORMAT)
            except ValueError:
                try:
                    end_date = datetime.datetime.strptime(tf_final_date.value, "%Y-%m-%d")
                except ValueError:
                    end_date = datetime.datetime.strptime('1900-01-01', "%Y-%m-%d")
        tf_final_date.value = end_date.strftime(DATE_FORMAT)
            
        if sw_reverse.value:
            work_days = holidays.backward_work_days(
                end_day=end_date,
                days=int(tf_days.value),
            )
            text_result = (
                f"{work_days.item().strftime(DATE_FORMAT)}, "
                f"{tf_days.value} dias úteis."
            )
        else:
            work_days = holidays.work_days(
                end_day=end_date,
                days=int(tf_days.value),
            )
            start_date = (
                end_date - datetime.timedelta(days=int(tf_days.value) - 1)
            ).strftime(DATE_FORMAT)
            text_result = (
                f'{work_days} dias úteis ({start_date} '
                f'- {end_date.strftime(DATE_FORMAT)})'
            )

        txt_work_days_result.value = text_result
        holidays_update_calendar(end_date)
        page.update()

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 10
    page.auto_scroll = True
    page.on_keyboard_event = on_keyboard

    final_date = datetime.datetime.today()
    # final_date = datetime.datetime(
    #     2023, 2, 28, 0, 0, 0, 0, datetime.timezone.utc
    # )

    txt_work_days_result = ft.Text(
        style=ft.TextThemeStyle.TITLE_MEDIUM,
        color=ft.colors.INDIGO_900,
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.BOLD,
    )
    tf_final_date = ft.TextField(
        label="Data Final",
        icon=ft.icons.CALENDAR_MONTH,
        value=final_date.strftime(DATE_FORMAT), width=180
    )

    tf_days = ft.TextField(
        label="Dias",
        icon=ft.icons.CALENDAR_TODAY,
        value='30', width=100
    )
    sw_reverse = ft.Switch(label="Dias futuros", value=True)
    bt_calc = ft.ElevatedButton(
        text="Calcular",
        color=ft.colors.BACKGROUND,
        bgcolor=ft.colors.BLUE_ACCENT,
        on_click=button_calcular_clicked,
    )

    main_menu_1 = ft.Row(
        [
            icon_image,
            tf_final_date,
            tf_days,
        ],
        wrap=True,
    )
    main_menu_2 = ft.Row(
        [
            sw_reverse, bt_calc,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    main_menu_3 = ft.Row(
        [
            ft.Text(''),
            txt_work_days_result,
        ],
        wrap=True,
    )

    page.add(
        ft.Container(
            content=main_menu_1,
            alignment=ft.alignment.center,
        ),
        ft.Container(
            content=main_menu_2,
            alignment=ft.alignment.center,
        ),
        ft.Container(
            content=main_menu_3,
            alignment=ft.alignment.center,
        )
    )
    
    button_calcular_clicked(None)
    tf_days.focus()
    page.update()


# ft.app(target=main, assets_dir="assets",)
ft.app(
    target=main, port=8550,
    view=ft.WEB_BROWSER,
    assets_dir="assets",
)
