"""
AIFlow Protocol Validator
验证分析结果是否符合 analysis-schema-v1.0.0.json 标准

核心功能:
1. JSON Schema 标准验证
2. 引用完整性检查
3. 时间戳格式验证
4. UUID 格式验证
5. 执行序号唯一性验证
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

try:
    from jsonschema import Draft7Validator, ValidationError, validators
except ImportError:
    raise ImportError(
        "jsonschema is required. Install with: pip install jsonschema"
    )


class ValidationResult:
    """验证结果"""

    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str) -> None:
        """添加错误"""
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """添加警告"""
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

    def __str__(self) -> str:
        if self.is_valid:
            return f"✅ Validation passed ({len(self.warnings)} warnings)"
        return f"❌ Validation failed ({len(self.errors)} errors, {len(self.warnings)} warnings)"


class ProtocolValidator:
    """协议验证器"""

    # ISO 8601 时间戳正则 (支持毫秒和时区)
    ISO_8601_PATTERN = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$"
    )

    # 文件路径:行号格式
    LOCATION_PATTERN = re.compile(r"^.+:\d+$")

    def __init__(self, schema_path: Optional[Path] = None):
        """
        初始化验证器

        Args:
            schema_path: JSON Schema 文件路径 (默认使用内置路径)
        """
        if schema_path is None:
            # 默认路径: contracts/analysis-schema-v1.0.0.json
            schema_path = Path(__file__).parent.parent.parent.parent / "contracts" / "analysis-schema-v1.0.0.json"

        self.schema_path = schema_path
        self.schema: Dict[str, Any] = self._load_schema()
        self.validator = Draft7Validator(self.schema)

    def _load_schema(self) -> Dict[str, Any]:
        """加载 JSON Schema"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_complete(self, data: Dict[str, Any]) -> ValidationResult:
        """
        完整验证入口

        执行顺序:
        1. JSON Schema 标准验证
        2. 时间戳格式验证
        3. UUID 格式验证
        4. 引用完整性检查
        5. 执行序号唯一性验证
        """
        result = ValidationResult()

        # 1. JSON Schema 标准验证
        schema_errors = self._validate_schema(data)
        for error in schema_errors:
            result.add_error(f"Schema validation: {error}")

        # 如果基础Schema验证失败，后续检查可能不准确
        if schema_errors:
            result.add_warning(
                "Skipping advanced validation due to schema errors"
            )
            return result

        # 2. 时间戳格式验证
        timestamp_errors = self._validate_timestamps(data)
        for error in timestamp_errors:
            result.add_error(f"Timestamp validation: {error}")

        # 3. UUID 格式验证
        uuid_errors = self._validate_uuids(data)
        for error in uuid_errors:
            result.add_error(f"UUID validation: {error}")

        # 4. 引用完整性检查
        ref_errors, ref_warnings = self._validate_references(data)
        for error in ref_errors:
            result.add_error(f"Reference integrity: {error}")
        for warning in ref_warnings:
            result.add_warning(f"Reference integrity: {warning}")

        # 5. 执行序号唯一性验证
        order_errors = self._validate_execution_order(data)
        for error in order_errors:
            result.add_error(f"Execution order: {error}")

        return result

    def _validate_schema(self, data: Dict[str, Any]) -> List[str]:
        """JSON Schema 标准验证"""
        errors = []
        for error in self.validator.iter_errors(data):
            path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")
        return errors

    def _validate_timestamps(self, data: Dict[str, Any]) -> List[str]:
        """验证 ISO 8601 时间戳格式"""
        errors = []

        def check_timestamp(value: Any, path: str) -> None:
            if isinstance(value, str):
                if not self.ISO_8601_PATTERN.match(value):
                    errors.append(f"{path}: Invalid ISO 8601 timestamp '{value}'")

        # 检查 project_metadata.analyzed_at
        if "project_metadata" in data:
            analyzed_at = data["project_metadata"].get("analyzed_at")
            if analyzed_at:
                check_timestamp(analyzed_at, "project_metadata.analyzed_at")

        # 检查 execution_trace 中的所有 timestamp
        if "execution_trace" in data:
            for unit_idx, unit in enumerate(data["execution_trace"].get("traceable_units", [])):
                for trace_idx, trace in enumerate(unit.get("traces", [])):
                    if trace.get("format") == "step-by-step":
                        trace_data = trace.get("data", {})

                        # 检查 steps
                        for step_idx, step in enumerate(trace_data.get("steps", [])):
                            ts = step.get("timestamp")
                            if ts:
                                check_timestamp(
                                    ts,
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.steps[{step_idx}].timestamp"
                                )

                        # 检查 variableScopes
                        for scope_idx, scope in enumerate(trace_data.get("variableScopes", [])):
                            ts = scope.get("timestamp")
                            if ts:
                                check_timestamp(
                                    ts,
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.variableScopes[{scope_idx}].timestamp"
                                )

                            # 检查 variables 的 history
                            for var_idx, var in enumerate(scope.get("variables", [])):
                                for hist_idx, hist in enumerate(var.get("history", [])):
                                    hist_ts = hist.get("timestamp")
                                    if hist_ts:
                                        check_timestamp(
                                            hist_ts,
                                            f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.variableScopes[{scope_idx}].variables[{var_idx}].history[{hist_idx}].timestamp"
                                        )

                        # 检查 callStack
                        for frame_idx, frame in enumerate(trace_data.get("callStack", [])):
                            ts = frame.get("timestamp")
                            if ts:
                                check_timestamp(
                                    ts,
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.callStack[{frame_idx}].timestamp"
                                )

        return errors

    def _validate_uuids(self, data: Dict[str, Any]) -> List[str]:
        """验证 UUID v4 格式"""
        errors = []

        def check_uuid(value: Any, path: str, field_name: str = "id") -> None:
            if isinstance(value, str):
                try:
                    uuid_obj = UUID(value, version=4)
                    # 验证是否为 UUID v4
                    if str(uuid_obj) != value:
                        errors.append(f"{path}.{field_name}: '{value}' is not a valid UUID v4")
                except ValueError:
                    errors.append(f"{path}.{field_name}: '{value}' is not a valid UUID format")

        # 检查 code_structure.nodes
        if "code_structure" in data:
            for node_idx, node in enumerate(data["code_structure"].get("nodes", [])):
                node_id = node.get("id")
                if node_id:
                    check_uuid(node_id, f"code_structure.nodes[{node_idx}]")

        # 检查 execution_trace
        if "execution_trace" in data:
            for unit_idx, unit in enumerate(data["execution_trace"].get("traceable_units", [])):
                unit_id = unit.get("id")
                if unit_id:
                    check_uuid(unit_id, f"execution_trace.traceable_units[{unit_idx}]")

                for trace_idx, trace in enumerate(unit.get("traces", [])):
                    if trace.get("format") == "step-by-step":
                        trace_data = trace.get("data", {})

                        # 检查 steps
                        for step_idx, step in enumerate(trace_data.get("steps", [])):
                            step_id = step.get("id")
                            if step_id:
                                check_uuid(
                                    step_id,
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.steps[{step_idx}]"
                                )

                        # 检查 variableScopes
                        for scope_idx, scope in enumerate(trace_data.get("variableScopes", [])):
                            scope_id = scope.get("id")
                            if scope_id:
                                check_uuid(
                                    scope_id,
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.variableScopes[{scope_idx}]"
                                )

                        # 检查 callStack
                        for frame_idx, frame in enumerate(trace_data.get("callStack", [])):
                            frame_id = frame.get("id")
                            if frame_id:
                                check_uuid(
                                    frame_id,
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.callStack[{frame_idx}]"
                                )

        return errors

    def _validate_references(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        验证引用完整性

        检查项:
        - LaunchButton.node_id → CodeNode.id
        - CodeEdge.source/target → CodeNode.id
        - CodeNode.parent → CodeNode.id
        - ExecutionStep.scope_id → VariableScope.id
        - VariableScope.parent_scope_id → VariableScope.id
        - StackFrame.local_scope_id → VariableScope.id
        - StackFrame.parent_frame_id → StackFrame.id
        - ConcurrencyFlow.start_point/end_point → CodeNode.id
        - ConcurrencyFlow.involved_units → TraceableUnit.id
        - SyncPoint.waiting_flows → ConcurrencyFlow.id
        """
        errors = []
        warnings = []

        # 收集所有 ID
        node_ids: Set[str] = set()
        traceable_unit_ids: Set[str] = set()
        scope_ids: Set[str] = set()
        frame_ids: Set[str] = set()
        flow_ids: Set[str] = set()

        # 收集 CodeNode IDs
        if "code_structure" in data:
            for node in data["code_structure"].get("nodes", []):
                node_id = node.get("id")
                if node_id:
                    node_ids.add(node_id)

        # 收集 TraceableUnit IDs, VariableScope IDs, StackFrame IDs
        if "execution_trace" in data:
            for unit in data["execution_trace"].get("traceable_units", []):
                unit_id = unit.get("id")
                if unit_id:
                    traceable_unit_ids.add(unit_id)

                for trace in unit.get("traces", []):
                    if trace.get("format") == "step-by-step":
                        trace_data = trace.get("data", {})

                        for scope in trace_data.get("variableScopes", []):
                            scope_id = scope.get("id")
                            if scope_id:
                                scope_ids.add(scope_id)

                        for frame in trace_data.get("callStack", []):
                            frame_id = frame.get("id")
                            if frame_id:
                                frame_ids.add(frame_id)

        # 收集 ConcurrencyFlow IDs
        if "concurrency_info" in data:
            for flow in data["concurrency_info"].get("flows", []):
                flow_id = flow.get("id")
                if flow_id:
                    flow_ids.add(flow_id)

        # 验证 LaunchButton.node_id
        if "behavior_metadata" in data:
            for btn_idx, btn in enumerate(data["behavior_metadata"].get("launch_buttons", [])):
                node_id = btn.get("node_id")
                if node_id and node_id not in node_ids:
                    errors.append(
                        f"behavior_metadata.launch_buttons[{btn_idx}].node_id '{node_id}' references non-existent CodeNode"
                    )

        # 验证 CodeEdge.source/target
        if "code_structure" in data:
            for edge_idx, edge in enumerate(data["code_structure"].get("edges", [])):
                source = edge.get("source")
                target = edge.get("target")
                if source and source not in node_ids:
                    errors.append(
                        f"code_structure.edges[{edge_idx}].source '{source}' references non-existent CodeNode"
                    )
                if target and target not in node_ids:
                    errors.append(
                        f"code_structure.edges[{edge_idx}].target '{target}' references non-existent CodeNode"
                    )

            # 验证 CodeNode.parent
            for node_idx, node in enumerate(data["code_structure"].get("nodes", [])):
                parent = node.get("parent")
                if parent and parent not in node_ids:
                    errors.append(
                        f"code_structure.nodes[{node_idx}].parent '{parent}' references non-existent CodeNode"
                    )

        # 验证 execution_trace 引用
        if "execution_trace" in data:
            for unit_idx, unit in enumerate(data["execution_trace"].get("traceable_units", [])):
                for trace_idx, trace in enumerate(unit.get("traces", [])):
                    if trace.get("format") == "step-by-step":
                        trace_data = trace.get("data", {})

                        # 验证 ExecutionStep.scope_id
                        for step_idx, step in enumerate(trace_data.get("steps", [])):
                            scope_id = step.get("scope_id")
                            if scope_id and scope_id not in scope_ids:
                                errors.append(
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.steps[{step_idx}].scope_id '{scope_id}' references non-existent VariableScope"
                                )

                        # 验证 VariableScope.parent_scope_id
                        for scope_idx, scope in enumerate(trace_data.get("variableScopes", [])):
                            parent_scope_id = scope.get("parent_scope_id")
                            if parent_scope_id and parent_scope_id not in scope_ids:
                                errors.append(
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.variableScopes[{scope_idx}].parent_scope_id '{parent_scope_id}' references non-existent VariableScope"
                                )

                        # 验证 StackFrame 引用
                        for frame_idx, frame in enumerate(trace_data.get("callStack", [])):
                            local_scope_id = frame.get("local_scope_id")
                            if local_scope_id and local_scope_id not in scope_ids:
                                errors.append(
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.callStack[{frame_idx}].local_scope_id '{local_scope_id}' references non-existent VariableScope"
                                )

                            parent_frame_id = frame.get("parent_frame_id")
                            if parent_frame_id and parent_frame_id not in frame_ids:
                                errors.append(
                                    f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}].data.callStack[{frame_idx}].parent_frame_id '{parent_frame_id}' references non-existent StackFrame"
                                )

        # 验证 ConcurrencyFlow 引用
        if "concurrency_info" in data:
            for flow_idx, flow in enumerate(data["concurrency_info"].get("flows", [])):
                start_point = flow.get("start_point")
                end_point = flow.get("end_point")

                if start_point and start_point not in node_ids:
                    errors.append(
                        f"concurrency_info.flows[{flow_idx}].start_point '{start_point}' references non-existent CodeNode"
                    )
                if end_point and end_point not in node_ids:
                    errors.append(
                        f"concurrency_info.flows[{flow_idx}].end_point '{end_point}' references non-existent CodeNode"
                    )

                # 验证 involved_units
                for unit_id in flow.get("involved_units", []):
                    if unit_id not in traceable_unit_ids:
                        warnings.append(
                            f"concurrency_info.flows[{flow_idx}].involved_units contains '{unit_id}' which references non-existent TraceableUnit"
                        )

            # 验证 SyncPoint.waiting_flows
            for sync_idx, sync in enumerate(data["concurrency_info"].get("sync_points", [])):
                for flow_id in sync.get("waiting_flows", []):
                    if flow_id not in flow_ids:
                        errors.append(
                            f"concurrency_info.sync_points[{sync_idx}].waiting_flows contains '{flow_id}' which references non-existent ConcurrencyFlow"
                        )

        return errors, warnings

    def validate_references(self, data: Dict[str, Any]) -> ValidationResult:
        """
        公开接口：单独验证引用完整性

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()
        ref_errors, ref_warnings = self._validate_references(data)

        for error in ref_errors:
            result.add_error(error)
        for warning in ref_warnings:
            result.add_warning(warning)

        return result

    def _validate_execution_order(self, data: Dict[str, Any]) -> List[str]:
        """验证 execution_order 全局唯一递增"""
        errors = []

        if "execution_trace" not in data:
            return errors

        for unit_idx, unit in enumerate(data["execution_trace"].get("traceable_units", [])):
            for trace_idx, trace in enumerate(unit.get("traces", [])):
                if trace.get("format") != "step-by-step":
                    continue

                trace_data = trace.get("data", {})
                execution_orders: List[int] = []

                # 收集所有 execution_order
                for step in trace_data.get("steps", []):
                    order = step.get("execution_order")
                    if order is not None:
                        execution_orders.append(order)

                for scope in trace_data.get("variableScopes", []):
                    order = scope.get("execution_order")
                    if order is not None:
                        execution_orders.append(order)

                for frame in trace_data.get("callStack", []):
                    order = frame.get("execution_order")
                    if order is not None:
                        execution_orders.append(order)

                # 检查唯一性
                if len(execution_orders) != len(set(execution_orders)):
                    duplicates = [
                        order for order in execution_orders
                        if execution_orders.count(order) > 1
                    ]
                    errors.append(
                        f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}]: Duplicate execution_order values found: {set(duplicates)}"
                    )

                # 检查递增 (排序后应与原列表相同)
                if execution_orders != sorted(execution_orders):
                    errors.append(
                        f"execution_trace.traceable_units[{unit_idx}].traces[{trace_idx}]: execution_order values are not monotonically increasing"
                    )

        return errors


def validate_analysis_result(
    data: Dict[str, Any],
    schema_path: Optional[Path] = None
) -> ValidationResult:
    """
    便捷函数：验证分析结果

    Args:
        data: 待验证的分析结果数据
        schema_path: JSON Schema 文件路径（可选）

    Returns:
        ValidationResult: 验证结果对象
    """
    validator = ProtocolValidator(schema_path)
    return validator.validate_complete(data)


# CLI 入口（用于测试）
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validator.py <analysis_result.json>")
        sys.exit(1)

    result_file = Path(sys.argv[1])
    if not result_file.exists():
        print(f"Error: File not found: {result_file}")
        sys.exit(1)

    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = validate_analysis_result(data)
    print(result)
    print()

    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")
        print()

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    sys.exit(0 if result.is_valid else 1)
