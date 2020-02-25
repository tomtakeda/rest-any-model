import json

from django.views import View
from autorest import response, filters
from autorest.response import JSONResponseMixin

from django.apps import apps


class AnyModelRestView(JSONResponseMixin, View):

    model = None
    model_name = None
    model_fields = set()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        model_name = kwargs.get('model_name', None)
        all_models = apps.all_models['autorest']
        self.model = all_models.get(model_name)
        self.model_name = model_name
        if self.model:
            self.model_fields = {field.name for field in self.model._meta.fields}

    def dispatch(self, request, *args, **kwargs):
        if not self.model:
            return self.render_to_response(response.fail(404, f"No such model <{self.model_name}>."))

        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get(self, request, *args, **kwargs):

        query = self.model.objects

        id = kwargs.get('id', None)
        if id:
            query = query.filter(pk=id)

        filters_param = request.GET.get('filter')
        if filters_param:
            for filter in json.loads(filters_param):
                prepared_filter = {}
                prepared_filter.update({
                    filters.get_filter_property(filter['property'], filter['operator']): filter['value']
                })
                query = query.filter(**prepared_filter)

        orders_param = request.GET.get('order')
        if orders_param:
            orders = json.loads(orders_param)
            for order in orders:
                field = order.get('property')
                direction = order.get('direction')
                if direction.upper() == 'DESC':
                    field = '-' + field

                query = query.order_by(field)

        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0)) + offset

        if limit:
            result = list(query.values()[offset:limit])
        else:
            result = list(query.values())

        return self.render_to_response(response.success(result))

    def post(self, request, *args, **kwargs):
        objects_param = request.body
        if objects_param:
            objects = json.loads(objects_param)
            inserts = 0
            for obj in objects:
                inst = self.model(**obj)
                inst.save()
                inserts += 1

        return self.render_to_response(response.success({"inserts": inserts}))

    def put(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        if not id:
            return self.render_to_response(response.fail(404, f"Nothing to update with id <{id}>"))

        for inst in self.model.objects.filter(pk=id):
            fields = json.loads(request.body)
            for name, value in fields.items():
                if getattr(inst, name):
                    setattr(inst, name, value)
            inst.save()

        return self.render_to_response(response.success("OK"))

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        if id:
            for inst in self.model.objects.filter(pk=id):
                inst.delete()

        return self.render_to_response(response.success("OK"))
