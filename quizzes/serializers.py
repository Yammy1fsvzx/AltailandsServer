from rest_framework import serializers
from .models import Quiz, Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'order']
        read_only_fields = ['id']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'answers']
        read_only_fields = ['id']

class QuizSerializer(serializers.ModelSerializer):
    # Используем QuestionSerializer для вложенного представления вопросов
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'slug', 'description', 'is_active',
            'created_at', 'updated_at', 'questions'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'questions']
        # Примечание: Создание/обновление вопросов и ответов через этот сериализатор
        # потребует кастомной логики в методах create/update сериализатора или ViewSet.
        # Пока мы делаем их read_only для простоты. 