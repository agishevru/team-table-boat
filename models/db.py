""" Модели для Алхимии. Работает через aiosqlite """


from sqlalchemy import Column, Integer, String, DateTime, JSON, select
from sqlalchemy.orm import declarative_base



Base = declarative_base()

class Users(Base):
    """ Карточка пользователя """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    time = Column(String)

class UrlGoogleSheets_month(Base):
    """ Ссылки на таблицы по месяцам """
    __tablename__ = 'url_google_sheets'

    month = Column(String, primary_key=True)
    url_google_sheets = Column(String)
    path_file = Column(String)

class TableParameters(Base):
    """ Параметры поиска: строка даты, первый столбец даты, столбец сотрудников """
    __tablename__ = 'table_parameters'
    id = Column(Integer, primary_key=True)
    date_row = Column(String)
    date_column_start = Column(String)
    employees_column = Column(String)


class GroupId(Base):
    """ Группа для рассылок """
    __tablename__ = 'group_ids'

    group_id = Column(Integer, primary_key=True)
    date = Column(String)
