from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follower, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeDisplaySerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionCreateSerializer,
                          SubscriptionSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = CustomLimitPagination

    def get_serializer_class(self):
        if self.action == ('list', 'retrieve'):
            return RecipeDisplaySerializer
        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):

        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = Favorite.objects.filter(user=request.user,
                                               recipe=recipe)
            if not favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            cart_item = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            )
            if not cart_item.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = Ingredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'name', 'measurement_unit'
        ).annotate(total_amount=Sum('recipe_ingredients__amount'))

        content = ''
        for ingredient in ingredients:
            content += (
                '{name} ({measurement_unit}) - {total_amount}\n'.format(
                    name=ingredient["name"],
                    measurement_unit=ingredient["measurement_unit"],
                    total_amount=ingredient["total_amount"]
                )
            )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для пользователей."""

    @action(detail=False, methods=('get',), url_path='me',
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=('get',), url_path='subscriptions')
    def subscriptions(self, request):
        """Метод для получения списка подписок."""
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        paginator = CustomLimitPagination()
        paginator_queryset = paginator.paginate_queryset(subscriptions,
                                                         request)
        serializer = SubscriptionSerializer(paginator_queryset, many=True,
                                            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'), url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        """Метод для подписки и отписки."""
        user = request.user
        user_to_subscribe = self.get_object()

        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': user.id, 'author': user_to_subscribe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Follower.objects.filter(user=user,
                                                   author=user_to_subscribe)
            if not subscription.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response({'status': 'Вы успешно отписались.'},
                            status=status.HTTP_204_NO_CONTENT)
