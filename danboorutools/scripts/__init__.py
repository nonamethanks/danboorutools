import ast
from typing import Generic, TypeVar

from peewee import DoesNotExist, Model, SqliteDatabase, TextField

ProgressValue = TypeVar("ProgressValue")


_progress_database = SqliteDatabase("data/progress.sqlite")


class _ProgressModel(Model):
    class Meta:
        database = _progress_database

    name = TextField(unique=True, primary_key=True, index=True)
    value = TextField()


class ProgressTracker(Generic[ProgressValue]):
    def __init__(self, name: str, default_value: ProgressValue) -> None:
        self.name = name
        self.default_value = default_value
        if isinstance(self.default_value, (dict, list, set)):
            self.cast_value = ast.literal_eval
        else:
            self.cast_value = type(self.default_value)

    @_progress_database.connection_context()
    def _init_database(self) -> None:
        with _progress_database:
            _progress_database.create_tables([_ProgressModel])

    @property
    def value(self) -> ProgressValue:
        self._init_database()
        try:
            row = _ProgressModel.get(_ProgressModel.name == self.name)
        except DoesNotExist:
            return self.default_value
        else:
            return self.cast_value(row.value)

    @value.setter
    def value(self, value: ProgressValue) -> None:
        self._init_database()
        _ProgressModel.replace(name=self.name, value=value).execute()

    @value.deleter
    def value(self) -> None:
        _ProgressModel.delete().where(_ProgressModel.name == self.name).execute()
