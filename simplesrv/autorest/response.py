from django.http import JsonResponse


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


def _response(data=None, error_code=None, error_msg=''):
    resp = {
        'data': data
    }
    if error_code or error_msg:
        resp.update({
            'error': {
                'code': error_code,
                'msg': error_msg
            }
        })
    return resp


def success(data):
    return _response(data)


def fail(code, msg):
    return _response(error_code=code, error_msg=msg)
