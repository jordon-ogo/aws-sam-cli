from .TemplateResource import TemplateResource


class EventSourceMapping(TemplateResource):
    def __init__(self, resource_object, resource_type, resource_name):
        super().__init__(resource_object, resource_type, resource_name)
