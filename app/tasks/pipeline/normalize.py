from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Literal
import json
import re

from app.schemas.collection_task.task_template import ProblemRecord, StorageColumnMapping


NormalizeTargetLayer = Literal["data_type", "physical"]


def normalize_rows(raw_rows: list[dict[str, Any]], column_mappings: list[StorageColumnMapping], target_layer: NormalizeTargetLayer = "data_type") -> tuple[list[dict[str, Any]], list[ProblemRecord]]:
    """
    根据 column_mappings 对采集后数据做字段映射、类型转换和唯一键检查。
    
    默认输出 data_type 层字段： 

        source_field_code -> data_type_field_code 
        source_field_type -> data_type_field_type 
        
    如果 target_layer="physical"，则直接输出物理表字段：

        data_type_field_code -> physical_column_name 
        data_type_field_type -> physical_column_type
    """

    if not column_mappings:
        raise ValueError("column_mappings 不能为空")

    if target_layer not in {"data_type", "physical"}:
        raise ValueError(f"不支持的 target_layer: {target_layer}")

    normalized_rows: list[dict[str, Any]] = []
    problems: list[ProblemRecord] = []

    # 唯一键字段列表
    unique_fields = [
        col.data_type_field_code if target_layer == "data_type" else col.physical_column_name
        for col in column_mappings if col.unique_key
    ]
    # 记录唯一键值，检查重复，同时记录首次出现行号
    seen_unique_keys: dict[tuple[Any, ...], int] = {}

    # 对每一行数据进行字段映射和类型转换
    for row_no, raw_row in enumerate(raw_rows, start=1):
        normalized_row: dict[str, Any] = {}
        row_valid = True

        for col in column_mappings:
            source_field = col.source_field_code if target_layer == "data_type" else col.data_type_field_code
            target_field = col.data_type_field_code if target_layer == "data_type" else col.physical_column_name
            target_type = col.data_type_field_type if target_layer == "data_type" else col.physical_column_type

            value = raw_row.get(source_field)
            required = col.required or col.unique_key

            if required and is_empty(value):
                row_valid = False
                problems.append(
                    ProblemRecord(
                        problem_type="NORMALIZE",
                        problem_message=f"必填字段为空: {source_field}",
                        sample_data_json={
                            "rowNo": row_no,
                            "field": source_field,
                            "rawData": raw_row,
                        },
                    )
                )
                continue

            if is_empty(value):
                normalized_row[target_field] = None
                continue

            try:
                normalized_row[target_field] = convert_value(value, target_type)
            except Exception as exc:
                row_valid = False
                problems.append(
                    ProblemRecord(
                        problem_type="NORMALIZE",
                        problem_message=(
                            f"字段类型转换失败: "
                            f"{source_field} -> {target_field}, "
                            f"target_type={target_type}, value={value}, error={exc}"
                        ),
                        sample_data_json={
                            "rowNo": row_no,
                            "field": source_field,
                            "rawData": raw_row,
                        },
                    )
                )

        if not row_valid:
            continue
        
        # 唯一键检查
        if unique_fields:
            unique_key = tuple(normalized_row.get(field) for field in unique_fields)

            if unique_key in seen_unique_keys:
                problems.append(
                    ProblemRecord(
                        problem_type="NORMALIZE",
                        problem_message=f"批次内唯一键重复，首次出现行号: {seen_unique_keys[unique_key]}",
                        sample_data_json={
                            "rowNo": row_no,
                            "field": ",".join(unique_fields),
                            "rawData": raw_row,
                        },
                    )
                )
            else:
                seen_unique_keys[unique_key] = row_no

        # 这里将重复的唯一键行也加入 normalized_rows，具体是否入库由后续清洗规则决定
        normalized_rows.append(normalized_row)

    return normalized_rows, problems


def convert_value(value: Any, field_type: str) -> Any:
    """
    将值转换为目标字段类型。

    field_type 既支持业务类型：
        STRING, DECIMAL, INT, DATE, DATETIME, BOOLEAN, JSON

    也兼容常见数据库类型：
        VARCHAR(20), NUMERIC(18,4), DECIMAL(18,4), BIGINT,
        DATE, TIMESTAMP, TIMESTAMP WITHOUT TIME ZONE
    """
    if is_empty(value):
        return None

    normalized_type = normalize_type_name(field_type)

    if normalized_type in {"STRING", "STR", "TEXT", "VARCHAR", "CHAR"}:
        return str(value)

    if normalized_type in {"DECIMAL", "NUMERIC", "NUMBER"}:
        return convert_decimal(value, field_type)

    if normalized_type in {"FLOAT", "DOUBLE", "REAL"}:
        return float(value)

    if normalized_type in {"INT", "INTEGER", "BIGINT", "SMALLINT"}:
        return int(Decimal(str(value)))

    if normalized_type in {"DATE"}:
        return convert_date(value)

    if normalized_type in {"DATETIME", "TIMESTAMP"}:
        return convert_datetime(value)

    if normalized_type in {"BOOL", "BOOLEAN"}:
        return convert_bool(value)

    if normalized_type in {"JSON", "JSONB", "DICT", "OBJECT"}:
        return convert_json(value)

    return value


def normalize_type_name(field_type: str) -> str:
    if not field_type:
        return "STRING"

    text = field_type.strip().upper()

    # NUMERIC(18,4) -> NUMERIC
    text = re.sub(r"\(.*\)", "", text).strip()

    # TIMESTAMP WITHOUT TIME ZONE -> TIMESTAMP
    if text.startswith("TIMESTAMP"):
        return "TIMESTAMP"

    # CHARACTER VARYING -> VARCHAR
    if text in {"CHARACTER VARYING", "CHAR VARYING"}:
        return "VARCHAR"

    return text


def convert_decimal(value: Any, field_type: str) -> Decimal:
    try:
        decimal_value = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"无法转换为 Decimal: {value}") from exc

    scale = extract_decimal_scale(field_type)
    if scale is None:
        return decimal_value

    quant = Decimal("1").scaleb(-scale)
    return decimal_value.quantize(quant, rounding=ROUND_HALF_UP)


def extract_decimal_scale(field_type: str) -> int | None:
    """
    从 NUMERIC(18,4)、DECIMAL(20,6) 中提取 scale。
    """
    if not field_type:
        return None

    match = re.search(r"\(\s*\d+\s*,\s*(\d+)\s*\)", field_type)
    if not match:
        return None

    return int(match.group(1))


def convert_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    text = str(value).strip()

    # Tushare trade_date: 20260522
    if len(text) == 8 and text.isdigit():
        return datetime.strptime(text, "%Y%m%d").date()

    # 2026-05-22
    return date.fromisoformat(text)


def convert_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    text = str(value).strip()

    # 20260522153000
    if len(text) == 14 and text.isdigit():
        return datetime.strptime(text, "%Y%m%d%H%M%S")

    # 20260522
    if len(text) == 8 and text.isdigit():
        return datetime.strptime(text, "%Y%m%d")

    # 兼容 2026-05-22T15:30:00Z
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    return datetime.fromisoformat(text)


def convert_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value != 0

    text = str(value).strip().lower()

    if text in {"true", "t", "yes", "y", "1"}:
        return True

    if text in {"false", "f", "no", "n", "0"}:
        return False

    raise ValueError(f"无法转换为 Boolean: {value}")


def convert_json(value: Any) -> Any:
    if isinstance(value, dict | list):
        return value

    if isinstance(value, str):
        return json.loads(value)

    return value


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False
