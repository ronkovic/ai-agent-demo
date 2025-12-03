"""Workflow Engine tests."""

import pytest

from agent_platform.services.workflow_engine import WorkflowContext, WorkflowEngine


class TestWorkflowContext:
    """Tests for WorkflowContext."""

    def test_init_with_no_trigger_data(self):
        """Test initialization without trigger data."""
        context = WorkflowContext()
        assert context.trigger_data == {}
        assert context._results == {}

    def test_init_with_trigger_data(self):
        """Test initialization with trigger data."""
        trigger_data = {"input": "test", "value": 42}
        context = WorkflowContext(trigger_data)
        assert context.trigger_data == trigger_data

    def test_set_and_get_result(self):
        """Test setting and getting node results."""
        context = WorkflowContext()
        context.set_result("node_1", {"output": "hello"})
        assert context.get_result("node_1") == {"output": "hello"}
        assert context.get_result("node_2") is None

    def test_to_dict(self):
        """Test converting context to dictionary."""
        trigger_data = {"input": "test"}
        context = WorkflowContext(trigger_data)
        context.set_result("node_1", {"output": "hello"})
        context.set_result("node_2", {"value": 42})

        result = context.to_dict()
        assert result["trigger"] == trigger_data
        assert result["node_1"] == {"output": "hello"}
        assert result["node_2"] == {"value": 42}


class TestWorkflowEngineDAG:
    """Tests for DAG construction and topological sort."""

    def test_build_dag_simple(self):
        """Test building a simple DAG."""
        nodes = [
            {"id": "a"},
            {"id": "b"},
            {"id": "c"},
        ]
        edges = [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
        ]

        engine = WorkflowEngine(db=None)
        dag = engine._build_dag(nodes, edges)

        assert "a" in dag
        assert "b" in dag
        assert "c" in dag
        assert dag["a"] == []
        assert dag["b"] == ["a"]
        assert dag["c"] == ["b"]

    def test_build_dag_with_multiple_inputs(self):
        """Test building a DAG with multiple inputs to a node."""
        nodes = [
            {"id": "a"},
            {"id": "b"},
            {"id": "c"},
        ]
        edges = [
            {"source": "a", "target": "c"},
            {"source": "b", "target": "c"},
        ]

        engine = WorkflowEngine(db=None)
        dag = engine._build_dag(nodes, edges)

        assert dag["c"] == ["a", "b"] or dag["c"] == ["b", "a"]

    def test_topological_sort_simple(self):
        """Test topological sort on a simple graph."""
        nodes = [
            {"id": "a"},
            {"id": "b"},
            {"id": "c"},
        ]
        dag = {
            "a": [],
            "b": ["a"],
            "c": ["b"],
        }

        engine = WorkflowEngine(db=None)
        result = engine._topological_sort(dag, nodes)

        assert result == ["a", "b", "c"]

    def test_topological_sort_parallel(self):
        """Test topological sort with parallel nodes."""
        nodes = [
            {"id": "a"},
            {"id": "b"},
            {"id": "c"},
            {"id": "d"},
        ]
        dag = {
            "a": [],
            "b": ["a"],
            "c": ["a"],
            "d": ["b", "c"],
        }

        engine = WorkflowEngine(db=None)
        result = engine._topological_sort(dag, nodes)

        # a must come first, d must come last
        assert result[0] == "a"
        assert result[-1] == "d"
        # b and c can be in any order between a and d
        assert set(result[1:3]) == {"b", "c"}

    def test_topological_sort_circular_dependency(self):
        """Test that circular dependencies are detected."""
        nodes = [
            {"id": "a"},
            {"id": "b"},
            {"id": "c"},
        ]
        dag = {
            "a": ["c"],  # a depends on c
            "b": ["a"],  # b depends on a
            "c": ["b"],  # c depends on b -> circular
        }

        engine = WorkflowEngine(db=None)
        with pytest.raises(ValueError, match="Circular dependency"):
            engine._topological_sort(dag, nodes)


class TestWorkflowEngineTemplates:
    """Tests for template resolution."""

    def test_resolve_template_simple(self):
        """Test simple template resolution."""
        context = WorkflowContext({"value": "hello"})
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template("{{trigger.value}}", context)
        assert result == "hello"

    def test_resolve_template_nested(self):
        """Test nested path resolution."""
        context = WorkflowContext({"data": {"nested": {"value": 42}}})
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template("{{trigger.data.nested.value}}", context)
        assert result == 42

    def test_resolve_template_with_node_result(self):
        """Test resolution with node results."""
        context = WorkflowContext()
        context.set_result("node_1", {"output": "world"})
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template("{{node_1.output}}", context)
        assert result == "world"

    def test_resolve_template_mixed(self):
        """Test mixed template with static text."""
        context = WorkflowContext({"name": "Alice"})
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template("Hello, {{trigger.name}}!", context)
        assert result == "Hello, Alice!"

    def test_resolve_template_multiple_placeholders(self):
        """Test template with multiple placeholders."""
        context = WorkflowContext({"first": "John", "last": "Doe"})
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template(
            "Name: {{trigger.first}} {{trigger.last}}", context
        )
        assert result == "Name: John Doe"

    def test_resolve_template_no_match(self):
        """Test template with non-existent path."""
        context = WorkflowContext({})
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template("{{trigger.missing}}", context)
        assert result is None

    def test_resolve_non_template_string(self):
        """Test that non-template strings are returned as-is."""
        context = WorkflowContext()
        engine = WorkflowEngine(db=None)

        result = engine._resolve_template("plain text", context)
        assert result == "plain text"


class TestWorkflowEngineConditions:
    """Tests for condition evaluation."""

    def test_condition_eq(self):
        """Test equality condition."""
        engine = WorkflowEngine(db=None)
        assert engine._evaluate_condition("hello", "eq", "hello") is True
        assert engine._evaluate_condition("hello", "eq", "world") is False

    def test_condition_ne(self):
        """Test not-equal condition."""
        engine = WorkflowEngine(db=None)
        assert engine._evaluate_condition("hello", "ne", "world") is True
        assert engine._evaluate_condition("hello", "ne", "hello") is False

    def test_condition_gt(self):
        """Test greater-than condition."""
        engine = WorkflowEngine(db=None)
        assert engine._evaluate_condition(10, "gt", 5) is True
        assert engine._evaluate_condition(5, "gt", 10) is False

    def test_condition_lt(self):
        """Test less-than condition."""
        engine = WorkflowEngine(db=None)
        assert engine._evaluate_condition(5, "lt", 10) is True
        assert engine._evaluate_condition(10, "lt", 5) is False

    def test_condition_contains(self):
        """Test contains condition."""
        engine = WorkflowEngine(db=None)
        assert engine._evaluate_condition("hello world", "contains", "world") is True
        assert engine._evaluate_condition("hello world", "contains", "foo") is False

    def test_condition_exists(self):
        """Test exists condition."""
        engine = WorkflowEngine(db=None)
        assert engine._evaluate_condition("value", "exists", None) is True
        assert engine._evaluate_condition(None, "exists", None) is False
