"""
Contributors: Aaron Antal-Bento (23013693)

Shared base helpers for repository classes."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from database_operations.database_context import execute_query


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class _SqlRepositoryHelpers:
    """Encapsulate SQL-building and identifier-validation helpers."""

    TABLE: str | None = None
    ID_FIELD: str | None = None

    @staticmethod
    def _validate_identifier(identifier: str) -> str:
        if not _IDENTIFIER_PATTERN.match(identifier):
            raise ValueError(f"Invalid SQL identifier: {identifier}")
        return identifier

    @classmethod
    def _build_select_columns(cls, columns: list[str] | None) -> str:
        if columns is None:
            return "*"

        if not columns:
            raise ValueError("Columns list cannot be empty.")

        if len(columns) == 1 and columns[0] == "*":
            return "*"

        return ", ".join(cls._validate_identifier(column) for column in columns)

    @classmethod
    def _build_order_by_clause(cls, order_by: str | None) -> str:
        if not order_by:
            return ""

        raw_parts = [part.strip() for part in order_by.split(",") if part.strip()]
        if not raw_parts:
            return ""

        normalized_parts: list[str] = []
        for part in raw_parts:
            tokens = part.split()

            if len(tokens) == 1:
                column = cls._validate_identifier(tokens[0])
                normalized_parts.append(column)
                continue

            if len(tokens) == 2 and tokens[1].upper() in {"ASC", "DESC"}:
                column = cls._validate_identifier(tokens[0])
                direction = tokens[1].upper()
                normalized_parts.append(f"{column} {direction}")
                continue

            raise ValueError(f"Invalid ORDER BY clause: {part}")

        return " ORDER BY " + ", ".join(normalized_parts)

    @classmethod
    def _resolve_identifier(
        cls,
        explicit: str | None,
        default: str | None,
        setting_name: str,
    ) -> str:
        value = explicit if explicit is not None else default
        if not value:
            raise ValueError(
                f"{setting_name} is required. Set {setting_name} on the repository or pass it explicitly."
            )
        return cls._validate_identifier(value)

    @classmethod
    def _resolve_table(cls, table: str | None = None) -> str:
        return cls._resolve_identifier(table, cls.TABLE, "TABLE")

    @classmethod
    def _resolve_id_field(cls, id_field: str | None = None) -> str:
        return cls._resolve_identifier(id_field, cls.ID_FIELD, "ID_FIELD")

    @classmethod
    def _build_select_query(
        cls,
        table_name: str,
        columns: list[str] | None = None,
        where_clause: str | None = None,
        order_by: str | None = None,
    ) -> str:
        select_columns = cls._build_select_columns(columns)
        query = f"SELECT {select_columns} FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += cls._build_order_by_clause(order_by)
        return query

    @staticmethod
    def _apply_allowed_fields(
        updates: dict[str, Any],
        allowed_fields: Iterable[str] | None,
    ) -> dict[str, Any]:
        if allowed_fields is None:
            return updates
        allowed = set(allowed_fields)
        return {field: value for field, value in updates.items() if field in allowed}

    @classmethod
    def _build_update_assignments(cls, updates: dict[str, Any]) -> tuple[str, list[Any]]:
        assignments: list[str] = []
        values: list[Any] = []
        for field, value in updates.items():
            assignments.append(f"{cls._validate_identifier(field)} = ?")
            values.append(value)
        return ", ".join(assignments), values


class BaseRepository(_SqlRepositoryHelpers):
    """Provide common CRUD utilities for concrete repositories."""

    TABLE: str | None = None
    ID_FIELD: str | None = None

    def _execute(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        return execute_query(query, params, fetch_one=fetch_one, fetch_all=fetch_all, commit=commit)

    def _insert(self, data: dict[str, Any], *, table: str | None = None):
        if not data:
            raise ValueError("Insert data cannot be empty.")

        table_name = self._resolve_table(table)
        columns = [self._validate_identifier(column) for column in data.keys()]
        placeholders = ", ".join(["?"] * len(columns))
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({placeholders})
        """
        return self._execute(query, tuple(data.values()), commit=True)

    def _update_by_id(
        self,
        id_value,
        updates: dict[str, Any],
        allowed_fields=None,
        *,
        table: str | None = None,
        id_field: str | None = None,
    ) -> bool:
        table_name = self._resolve_table(table)
        resolved_id_field = self._resolve_id_field(id_field)
        updates = self._apply_allowed_fields(updates, allowed_fields)

        if not updates:
            return False

        set_clause, params = self._build_update_assignments(updates)

        params.append(id_value)
        query = f"UPDATE {table_name} SET {set_clause} WHERE {resolved_id_field} = ?"
        result = self._execute(query, tuple(params), commit=True)
        return result is not None and result > 0

    def _delete_by_id(self, id_value, *, table: str | None = None, id_field: str | None = None) -> bool:
        table_name = self._resolve_table(table)
        resolved_id_field = self._resolve_id_field(id_field)
        query = f"DELETE FROM {table_name} WHERE {resolved_id_field} = ?"
        result = self._execute(query, (id_value,), commit=True)
        return result is not None and result > 0

    def _get_all(self, columns: list[str] | None = None, order_by: str | None = None, *, table: str | None = None):
        table_name = self._resolve_table(table)
        query = self._build_select_query(table_name, columns=columns, order_by=order_by)
        return self._execute(query, fetch_all=True)

    def _get_all_by_field(
        self,
        field_name: str,
        field_value,
        columns: list[str] | None = None,
        order_by: str | None = None,
        *,
        table: str | None = None,
    ):
        table_name = self._resolve_table(table)
        resolved_field_name = self._validate_identifier(field_name)
        query = self._build_select_query(
            table_name,
            columns=columns,
            where_clause=f"{resolved_field_name} = ?",
            order_by=order_by,
        )
        return self._execute(query, (field_value,), fetch_all=True)

    def _get_by_id(
        self,
        id_value,
        columns: list[str] | None = None,
        *,
        table: str | None = None,
        id_field: str | None = None,
    ):
        table_name = self._resolve_table(table)
        resolved_id_field = self._resolve_id_field(id_field)
        query = self._build_select_query(
            table_name,
            columns=columns,
            where_clause=f"{resolved_id_field} = ?",
        )
        return self._execute(query, (id_value,), fetch_one=True)

    def _get_count(self, id_value, *, table: str | None = None, id_field: str | None = None) -> int:
        table_name = self._resolve_table(table)
        resolved_id_field = self._resolve_id_field(id_field)
        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {resolved_id_field} = ?"
        result = self._execute(query, (id_value,), fetch_one=True)
        return result["count"] if result else 0