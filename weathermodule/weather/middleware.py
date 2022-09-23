from functools import wraps


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        if getattr(response, "deleteheaders", False):

            try:
                del response["Server"]
                del response["X-Frame-Options"]
                del response["X-Content-Type-Options"]
                del response["Referrer-Policy"]
                del response["Cross-Origin-Opener-Policy"]
                del response["X-Clacks-Overhead"]
            except: pass
            return response
        return response
        # Code to be executed for each request/response after
        # the view is called.



def headers_delete(view_func):
    """
    Modify a view function by setting a response variable that instructs
    XFrameOptionsMiddleware to NOT set the X-Frame-Options HTTP header. Usage:

    @xframe_options_exempt
    def some_view(request):
        ...
    """

    def wrapped_view(*args, **kwargs):
        resp = view_func(*args, **kwargs)
        resp.deleteheaders = True
        return resp

    return wraps(view_func)(wrapped_view)