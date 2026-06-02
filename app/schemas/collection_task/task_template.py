"""
任务模板相关数据模型（Pydantic）
与 Spring Boot 侧的 TaskTemplateSync 保持字段一致
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OutputField(BaseModel):
    """
    接口可返回字段描述
    字段编码（fieldCode）和路径（fieldPath）作为来源字段识别的主要依据
    """
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    field_code: str = Field(..., validation_alias="fieldCode", serialization_alias="fieldCode", description="字段编码")
    field_name: Optional[str] = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="字段名称（展示用）")
    field_type: str = Field(..., validation_alias="fieldType", serialization_alias="fieldType", description="字段类型，如 DATE/STRING/DECIMAL")
    required: Optional[bool] = Field(default=False, validation_alias="required", serialization_alias="required", description="是否必填")
    unique_key: Optional[bool] = Field(default=False, validation_alias="uniqueKey", serialization_alias="uniqueKey", description="是否业务唯一键")
    sort_no: Optional[int] = Field(default=None, validation_alias="sortNo", serialization_alias="sortNo", description="排序号")
    field_desc: Optional[str] = Field(default=None, validation_alias="fieldDesc", serialization_alias="fieldDesc", description="字段说明")


class TaskTemplateInfo(BaseModel):
    """
    任务模板信息
    任务处理层通过此结构向应用服务层上报当前支持的采集任务模板
    """
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    task_code: str = Field(..., validation_alias="taskCode", serialization_alias="taskCode", description="任务编码，全局唯一")
    task_name: str = Field(..., validation_alias="taskName", serialization_alias="taskName", description="任务名称")
    task_desc: Optional[str] = Field(default=None, validation_alias="taskDesc", serialization_alias="taskDesc", description="任务说明")
    handler_name: str = Field(..., validation_alias="handlerName", serialization_alias="handlerName", description="任务处理入口名称（Python 函数/类名）")
    data_source: Optional[str] = Field(default=None, validation_alias="dataSource", serialization_alias="dataSource", description="数据源标识")
    asset_type: Optional[str] = Field(default=None, validation_alias="assetType", serialization_alias="assetType", description="资产类型")
    biz_type: Optional[str] = Field(default=None, validation_alias="bizType", serialization_alias="bizType", description="业务分类")
    params_schema: List[OutputField] = Field(default_factory=list, validation_alias="paramsSchema", serialization_alias="paramsSchema", description="执行参数结构（JSON Schema）")
    output_fields: List[OutputField] = Field(default_factory=list, validation_alias="outputFields", serialization_alias="outputFields", description="接口可返回字段列表")
    rule_category_codes: Optional[List[str]] = Field(default=None, validation_alias="ruleCategoryCodes", serialization_alias="ruleCategoryCodes", description="可选规则类别编码列表")
    sync_time: Optional[datetime] = Field(default=None, validation_alias="syncTime", serialization_alias="syncTime", description="同步时间，默认取当前时间")


class CleaningRule(BaseModel):
    rule_id: str
    rule_version_id: str
    rule_type: str
    target_field: str | None = None
    rule_content: dict[str, Any] = Field(default_factory=dict)


class StorageColumnMapping(BaseModel):
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    storage_mapping_code: str = Field(..., validation_alias="storageMappingCode", serialization_alias="storageMappingCode")
    source_field_code: str = Field(..., validation_alias="sourceFieldCode", serialization_alias="sourceFieldCode")
    source_field_name: Optional[str] = Field(default=None, validation_alias="sourceFieldName", serialization_alias="sourceFieldName")
    source_field_type: str = Field(..., validation_alias="sourceFieldType", serialization_alias="sourceFieldType")
    data_type_field_code: str = Field(..., validation_alias="dataTypeFieldCode", serialization_alias="dataTypeFieldCode")
    data_type_field_type: str = Field(..., validation_alias="dataTypeFieldType", serialization_alias="dataTypeFieldType")
    physical_column_name: str = Field(..., validation_alias="physicalColumnName", serialization_alias="physicalColumnName")
    physical_column_type: str = Field(..., validation_alias="physicalColumnType", serialization_alias="physicalColumnType")
    default_value: Optional[str] = Field(default=None, validation_alias="defaultValue", serialization_alias="defaultValue")
    required: bool = Field(default=False, validation_alias="required", serialization_alias="required")
    unique_key: bool = Field(default=False, validation_alias="uniqueKey", serialization_alias="uniqueKey")


class StorageMapping(BaseModel):
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    storage_mapping_code: str = Field(..., validation_alias="storageMappingCode", serialization_alias="storageMappingCode")
    task_config_code: Optional[str] = Field(default=None, validation_alias="taskConfigCode", serialization_alias="taskConfigCode")
    physical_schema_name: str = Field(..., validation_alias="physicalSchemaName", serialization_alias="physicalSchemaName")
    physical_table_name: str = Field(..., validation_alias="physicalTableName", serialization_alias="physicalTableName")
    write_strategy: str = Field(default="UPSERT", validation_alias="writeStrategy", serialization_alias="writeStrategy")


class ExecutionContext(BaseModel):
    """
    执行上下文（由应用服务层下发，I-36）
    任务处理层根据此上下文完成采集、处理、校验和标准化输出
    """
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True, extra="allow")

    # task_template: Optional[Any] = Field(default=None, serialization_alias="taskTemplate", description="任务模板快照")
    task_config: Optional[Dict[str, Any]] = Field(default=None, validation_alias="taskConfig", serialization_alias="taskConfig", description="任务配置快照")
    params: Dict[str, Any] = Field(default_factory=dict, validation_alias="params", serialization_alias="params", description="执行参数")
    cron_expression: Optional[str] = Field(default=None, validation_alias="cronExpression", serialization_alias="cronExpression", description="调度表达式")
    storage_mapping: StorageMapping = Field(..., validation_alias="storageMapping", serialization_alias="storageMapping", description="存储映射详情")
    columns: List[StorageColumnMapping] = Field(default_factory=list, validation_alias="columns", serialization_alias="columns", description="存储字段映射明细")
    scheduled_fire_time: Optional[datetime] = Field(default=None, validation_alias="scheduledFireTime", serialization_alias="scheduledFireTime", description="调度触发时间")


class TaskRunRequest(BaseModel):
    """
    I-36 执行任务请求体（应用服务层 → 任务处理层）
    """
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)
    
    run_id: str = Field(..., validation_alias="runId", serialization_alias="runId", description="执行记录 ID")
    task_code: str = Field(..., validation_alias="taskCode", serialization_alias="taskCode", description="任务编码")
    task_template_version_no: int = Field(..., validation_alias="taskTemplateVersionNo", serialization_alias="taskTemplateVersionNo", description="任务模板版本号")
    handler_name: str = Field(..., validation_alias="handlerName", serialization_alias="handlerName", description="处理入口名称")
    execution_context: ExecutionContext = Field(..., validation_alias="executionContext", serialization_alias="executionContext", description="执行上下文")


class ProblemRecord(BaseModel):
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    problem_id: Optional[str] = Field(default=None, validation_alias="problemId", serialization_alias="problemId")
    run_id: Optional[str] = Field(default=None, validation_alias="runId", serialization_alias="runId")
    problem_type: Optional[str] = Field(default=None, validation_alias="problemType", serialization_alias="problemType")
    problem_message: Optional[str] = Field(default=None, validation_alias="problemMessage", serialization_alias="problemMessage")
    sample_data_json: Optional[Dict[str, Any]] = Field(default=None, validation_alias="sampleDataJson", serialization_alias="sampleDataJson")
    created_at: Optional[datetime] = Field(default=None, validation_alias="createdAt", serialization_alias="createdAt")


class ResultLocation(BaseModel):
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    physical_schema_name: str = Field(..., validation_alias="physicalSchemaName", serialization_alias="physicalSchemaName")
    physical_table_name: str = Field(..., validation_alias="physicalTableName", serialization_alias="physicalTableName")
    run_id: str = Field(..., validation_alias="runId", serialization_alias="runId")


class TaskRunResult(BaseModel):
    """
    I-36 执行结果返回体（任务处理层 → 应用服务层）
    """
    model_config = ConfigDict(validate_by_name=True, serialize_by_alias=True)

    run_id: str = Field(..., validation_alias="runId", serialization_alias="runId", description="执行记录 ID")
    status: str = Field(..., validation_alias="status", serialization_alias="status", description="执行状态，如 SUCCESS/FAILURE/PARTIAL_SUCCESS")
    total_count: int = Field(default=0, validation_alias="totalCount", serialization_alias="totalCount", description="总处理条数")
    success_count: int = Field(default=0, validation_alias="successCount", serialization_alias="successCount", description="成功条数")
    failure_count: int = Field(default=0, validation_alias="failureCount", serialization_alias="failureCount", description="失败条数")
    result_location: Optional[ResultLocation] = Field(default=None, validation_alias="resultLocation", serialization_alias="resultLocation", description="结果定位信息")
    summary_content: Optional[Dict[str, Any]] = Field(default=None, validation_alias="summaryContent", serialization_alias="summaryContent", description="结果摘要内容")
    # 运行时日志、问题样本和异常记录（供回调回传给 Spring Boot）
    logs: Optional[List[Dict[str, Any]]] = Field(default=None, validation_alias="logs", serialization_alias="logs", description="运行日志列表")
    problems: Optional[List[ProblemRecord]] = Field(default=None, validation_alias="problems", serialization_alias="problems", description="问题样本列表")
    exceptions: Optional[List[Dict[str, Any]]] = Field(default=None, validation_alias="exceptions", serialization_alias="exceptions", description="异常记录列表")


