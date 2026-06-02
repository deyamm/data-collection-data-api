from typing import Any

from app.schemas.collection_task.task_template import CleaningRule, ProblemRecord


def clean_rows(
    rows: list[dict[str, Any]],
    rules: list[CleaningRule],
) -> tuple[list[dict[str, Any]], list[ProblemRecord]]:
    """
    简化版清洗规则引擎。
    先支持：
    - NOT_NULL
    - GT_ZERO
    - NON_NEGATIVE

    后续可以把规则内容升级为表达式 DSL 或 Python 安全沙箱外置规则。
    """
    valid_rows: list[dict[str, Any]] = []
    problems: list[ProblemRecord] = []

    for idx, row in enumerate(rows, start=1):
        row_valid = True

        for rule in rules:
            field = rule.target_field or rule.rule_content.get("field")
            if not field:
                continue

            value = row.get(field)
            rule_type = rule.rule_type.upper()

            if rule_type == "NOT_NULL":
                if value in (None, ""):
                    row_valid = False
                    problems.append(
                        ProblemRecord(
                            problem_type="CLEAN",
                            problem_message=f"规则 {rule.rule_version_id} 校验失败：字段不能为空",
                            sample_data_json={
                                "rowNo": idx,
                                "field": field,
                                "rawData": row,
                            },
                        )
                    )

            elif rule_type == "GT_ZERO":
                if value is not None and value <= 0:
                    row_valid = False
                    problems.append(
                        ProblemRecord(
                            problem_type="CLEAN",
                            problem_message=f"规则 {rule.rule_version_id} 校验失败：字段必须大于 0",
                            sample_data_json={
                                "rowNo": idx,
                                "field": field,
                                "rawData": row,
                            },
                        )
                    )

            elif rule_type == "NON_NEGATIVE":
                if value is not None and value < 0:
                    row_valid = False
                    problems.append(
                        ProblemRecord(
                            problem_type="CLEAN",
                            problem_message=f"规则 {rule.rule_version_id} 校验失败：字段不能为负数",
                            sample_data_json={
                                "rowNo": idx,
                                "field": field,
                                "rawData": row,
                            },
                        )
                    )

        if row_valid:
            valid_rows.append(row)

    return valid_rows, problems
