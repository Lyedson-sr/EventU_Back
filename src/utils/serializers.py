from rest_framework.serializers import Serializer, CharField


class MessageResponseSerializer(Serializer):
    message = CharField()


class ErrorDetailResponseSerializer(Serializer):
    detail = CharField()
