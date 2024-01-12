import typing
from typing import Optional


class ChainBaseClass:
    def set_default_template(self, template: str, structure_template: Optional[str] = None) -> None:
        self.default_template = template
        # Check if the default template contains the "{structure_output_template}"
        if "{{ structure_output_template }}" in self.default_template:
            # If it does, then we need to replace it with the output template
            if structure_template is None:
                raise ValueError("If the default template contains the structure_output_template, "
                                 "then you must provide a structure template.")
            self.structure_output_template = structure_template
            self.default_template = self.default_template.replace(
                "{{ structure_output_template }}", self.structure_output_template
            )

    def _postprocess_response(self, out: dict) -> typing.Any:
        return out

    def __call__(self, *args, **kwargs):
        if not hasattr(self, "chain"):
            raise NotImplementedError("ChainBaseClass must be subclassed and the chain attribute must be set.")
        return self._postprocess_response(self.chain(*args, **kwargs))

    @property
    def template(self):
        return self.chain.prompt.template

    @template.setter
    def template(self, value):
        new_value = value
        # If the value contains the "{structure_output_template}", then we need to replace it with the output template
        if "{{ structure_output_template }}" in value:
            new_value = value.replace("{{ structure_output_template }}", self.structure_output_template)
        self.chain.prompt.template = new_value
