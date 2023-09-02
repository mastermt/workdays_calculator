import sqlite3
from typing import Any, List


def holidays_to_drop() -> List:

    holidays: list[tuple[str, str, str, str] | Any] = [
        ('2022-06-29', 'Feriado Municipal', 'Sorriso', 'MT'),
        ('2022-09-07', 'Independência do Brasil', '', ''),
        ('2022-10-12', 'Nossa Sra Aparecida', '', ''),
        ('2022-11-02', 'Finados', '', ''),
        ('2022-11-15', 'Proclamação da República', '', ''),
        ('2022-11-24', 'Expediente das ', '', ''),
        ('2022-11-28', 'Expediente das ', '', ''),
        ('2022-12-02', 'Expediente das ', '', ''),
        ('2022-12-05', 'Expediente das ', '', ''),
        ('2022-12-09', 'Expediente das ', '', ''),
        ('2022-12-23', 'Ponto Facultativo', '', ''),
        ('2022-12-25', 'Natal', '', ''),
        ('2022-12-30', 'Ponto Facultativo', '', ''),
        ('2023-01-01', 'Ano Novo', '', ''),
        ('2023-02-20', 'Ponto Facultativo-Carnaval', '', ''),
        ('2023-02-21', 'Ponto Facultativo-Carnaval', '', ''),
        ('2023-02-22', 'Ponto Facultativo-Carnaval', '', ''),
        ('2023-09-07', 'Independência do Brasil', '', ''),
    ]
    return holidays


def database_con(database_name: str):
    con = sqlite3.connect(database_name)
    return con


def cria_tabela() -> None:
    """

    :rtype: None
    """
    con = database_con("feriados.db")
    cur = con.cursor()

    # drop table holidays
    cur.execute("DROP TABLE IF EXISTS holidays")
    con.commit()

    query: str = """
        CREATE TABLE holidays(
            date CHAR(10) PRIMARY KEY,
            description CHAR(80) NOT NULL,
            city CHAR(50),
            state CHAR(2)
        )
    """
    cur.execute(query)

    query: str = """
        INSERT OR IGNORE INTO holidays
            (date, description, city, state)
            VALUES(?, ?, ?, ?)
    """
    cur.executemany(query, holidays_to_drop())
    con.commit()
    con.close()
