import re
from typing import Any, Dict, Generic, Literal, Optional, Self, TypeVar

from pydantic import BaseModel, Field

# Type variable for the partial model type
TPartial = TypeVar("TPartial", bound=BaseModel)
# Type variable for the base model type in ModelWithInputs


def render_obj(obj: Any, namespace: str, ctx: Dict[str, Any]) -> Any:
    if isinstance(obj, dict):
        return {k: render_obj(v, namespace, ctx) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [render_obj(v, namespace, ctx) for v in obj]
    elif isinstance(obj, str):
        # Replace ${{namespace.key}} with context[key]
        def replace_param(match):
            param_name = match.group(1)
            if param_name not in ctx:
                raise ValueError(f"Parameter '{param_name}' not found in context")
            return str(ctx[param_name])

        return re.sub(r"\$\{\{\s*" + namespace + r"\.(\w+)\s*\}\}", replace_param, obj)
    else:
        return obj


class Parameter(BaseModel):
    """
    Parameter definition for profile and mount configuration.
    """

    required: bool = Field(..., description="Whether this parameter is required.")
    type: Literal["string", "integer", "boolean", "float"] = Field(
        ..., description="The type of the parameter."
    )
    default: Optional[str | int | bool | float] = Field(
        default=None, description="Default value for the parameter."
    )


class ResolveableModel(BaseModel):
    """
    Mixin for Pydantic models to support ${{inputs.key}} placeholder resolution.
    Placeholders in string fields will be replaced with values from the context.

    If the model has a 'inputs' field (Dict[str, Parameter]), the context values
    are validated against the parameter definitions before resolution.
    """

    def resolve_placeholders(self, context: Dict[str, Any]) -> Self:
        model_data = self.model_dump()

        # Remove everything from the context that is not a defined input
        if "inputs" in model_data and isinstance(model_data["inputs"], dict):
            context = {k: v for k, v in context.items() if k in model_data["inputs"]}

        # Validate the type of context values against the Parameter definitions
        for key, value in context.items():
            if "inputs" in model_data and isinstance(model_data["inputs"], dict):
                param_def = model_data["inputs"].get(key)
                if param_def:
                    expected_type = param_def.get("type")
                    if expected_type == "string" and not isinstance(value, str):
                        raise TypeError(f"Parameter '{key}' expected to be string")
                    elif expected_type == "integer" and not isinstance(value, int):
                        raise TypeError(f"Parameter '{key}' expected to be integer")
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        raise TypeError(f"Parameter '{key}' expected to be boolean")
                    elif expected_type == "float" and not isinstance(value, float):
                        raise TypeError(f"Parameter '{key}' expected to be float")

        # Validate context against inputs if they exist
        if "inputs" in model_data and isinstance(model_data["inputs"], dict):
            for input_name, input_spec in model_data["inputs"].items():
                # Check if required input is missing
                if input_spec.get("required", False) and input_name not in context:
                    # Check if there's a default value
                    if input_spec.get("default") is not None:
                        context[input_name] = input_spec["default"]
                    else:
                        raise ValueError(f"Required input '{input_name}' is missing from context")
                # Add default value if input is not in context
                elif input_name not in context and input_spec.get("default") is not None:
                    context[input_name] = input_spec["default"]

        # Resolve all placeholders in the model
        resolved_dict = render_obj(model_data, "inputs", context)

        return self.__class__(**resolved_dict)


class MergeableModel(BaseModel, Generic[TPartial]):
    """
    Base model that supports merging another model into it.

    The merge creates a copy of the current model and updates its fields with values from
     `partial`, but only for fields that are set in the `partial` instance.
    """

    def merge(self, partial: TPartial | None) -> Self:
        """
        Merge another BaseModel into this one, returning a new instance.

        Args:
            partial (TPartial | None): The partial model to merge into this one.
                If None, returns a copy of the current instance.

        Returns:
            Self: A new instance of the model with merged values.
        """
        if partial is None:
            return self.model_copy()
        return self.model_copy(update=partial.model_dump(exclude_unset=True, exclude_none=True))
