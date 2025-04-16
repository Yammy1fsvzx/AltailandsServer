from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# Create your views here.

@extend_schema(
    tags=['Аутентификация'],
    summary="Выход из системы (добавление Refresh токена в черный список)",
    description="Принимает Refresh токен и добавляет его в черный список, делая его недействительным для последующего обновления Access токена.",
    request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}},
    responses={
        200: {'description': 'Токен успешно добавлен в черный список.'},
        400: {'description': 'Неверный формат запроса или невалидный токен.'},
        401: {'description': 'Пользователь не аутентифицирован.'}
    },
    examples=[
        OpenApiExample(
            'Пример запроса на выход',
            summary='Запрос с Refresh токеном',
            description='В теле запроса должен быть передан текущий Refresh токен.',
            value={"refresh": "<your_refresh_token>"}
        ),
    ]
)
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        try:
            refresh_token = request.data["refresh"]
            if not isinstance(refresh_token, str):
                 raise ValueError("Refresh token must be a string")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_200_OK, data={"detail": "Токен успешно добавлен в черный список."}) # Используем код 200 OK
        except KeyError:
            return Response({"error": "Refresh token не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Невалидный или истекший токен"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Ловим другие возможные ошибки
            return Response({"error": f"Произошла ошибка: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
