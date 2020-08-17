from rest_framework import generics, status
from rest_framework.response import Response

from pokerback.utils.baseobject import BaseObject


class BasicRequest(BaseObject):
    pass


class BasicResponse(BaseObject):
    pass


class BaseGetView(generics.GenericAPIView):
    def get_response_class(self):
        response_cls = getattr(self, "response_class")
        assert issubclass(response_cls, BaseObject)
        return response_cls

    def handle_request(self):
        raise NotImplemented

    def get(self, request, *args, **kwargs):
        response_obj = self.handle_request()

        try:
            response_json = response_obj.to_json()
        except Exception as e:
            print(e)
            return Response(
                "Response format is invalid.", status=status.HTTP_400_BAD_REQUEST
            )

        return Response(response_json, status=status.HTTP_200_OK)


class BasePostView(generics.GenericAPIView):
    def get_request_class(self):
        request_cls = getattr(self, "request_class")
        assert issubclass(request_cls, BaseObject)
        return request_cls

    def get_response_class(self):
        response_cls = getattr(self, "response_class")
        assert issubclass(response_cls, BaseObject)
        return response_cls

    def handle_request(self, request_obj):
        raise NotImplemented

    def post(self, request, *args, **kwargs):
        try:
            request_obj = self.get_request_class().from_json(request.data)
        except Exception as e:
            print(e)
            return Response(
                "Request format is invalid.", status=status.HTTP_400_BAD_REQUEST
            )

        response_obj = self.handle_request(request_obj)

        try:
            response_json = response_obj.to_json()
        except Exception as e:
            print(e)
            return Response(
                "Response format is invalid.", status=status.HTTP_400_BAD_REQUEST
            )

        return Response(response_json, status=status.HTTP_200_OK)
