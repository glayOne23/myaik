class FormErrorsMixin:
    def get_errors(self):
        ul = '<ul class="errorlist">'
        for field in self.visible_fields():
            if field.errors:
                ul += f'<li><strong>{field.label}:</strong> {field.errors}</li>'
        for error in self.non_field_errors():
            ul += f'<li><strong>Error:</strong> {error}</li>'
        ul += '</ul>'
        return ul