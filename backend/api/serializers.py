import base64
import re

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Follower

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Класс для загрузки изображения в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _, base64_str = data.split(';base64,')
            decoded_file = base64.b64decode(base64_str)
            file_extension = self.get_file_extension(data)
            filename = f'temp.{file_extension}'
            data = ContentFile(decoded_file, name=filename)
        return super().to_internal_value(data)

    def get_file_extension(self, data):
        return data.split(';')[0].split('/')[1]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов рецепта."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для отображения пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.following.filter(user=user).exists()
        return False


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')

    def validate_username(self, attrs):
        if not re.match(r'^[\w.@+-]+$', attrs):
            raise serializers.ValidationError(
                'Username должен состоять из букв, цифр и подчеркивания'
            )
        return attrs


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(source='recipe_ingredients',
                                             many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'image', 'cooking_time', 'ingredients',
                  'tags')

    def validation_on_create_update(self, validated_data):
        if not validated_data.get('tags'):
            raise serializers.ValidationError('Рецепт должен содержать теги.')
        if not validated_data.get('recipe_ingredients'):
            raise serializers.ValidationError(
                'Рецепт должен содержать ингредиенты.'
            )
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return tags, ingredients_data

    def add_ingredients_tags(self, recipe, tags, ingredients_data):
        unique_ingredients = set()
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient']['id']
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            unique_ingredients.add(ingredient_id)
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist as err:
                raise serializers.ValidationError(
                    'Ингредиента не существует.'
                ) from err
            amount = ingredient_data.get('amount')
            recipe_ingredients.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            ))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)
        return recipe

    def create(self, validated_data):

        tags, ingredients_data = self.validation_on_create_update(
            validated_data
        )
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)

        return self.add_ingredients_tags(
            recipe=recipe,
            tags=tags,
            ingredients_data=ingredients_data
        )

    def update(self, instance, validated_data):
        tags, ingredients_data = self.validation_on_create_update(
            validated_data
        )
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance = self.add_ingredients_tags(
            instance,
            tags,
            ingredients_data
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeDisplaySerializer(
            instance, context={'request': request}
        ).data


class RecipeDisplaySerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    ingredients = RecipeIngredientSerializer(source='recipe_ingredients',
                                             many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного отображения рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        method = self.context.get('method')
        recipe_user = Favorite.objects.filter(user=data['user'],
                                              recipe=data['recipe']).exists()
        if method == 'POST' and recipe_user:
            raise serializers.ValidationError(
                'Рецепт уже в Избранном.'
            )
        if method == 'DELETE' and not recipe_user:
            raise serializers.ValidationError(
                'Рецепта нет в Избранном.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSmallSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        method = self.context.get('method')
        recipe_user = ShoppingCart.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists()
        if method == 'POST' and recipe_user:
            raise serializers.ValidationError(
                'Рецепт уже в Корзине.'
            )
        if method == 'DELETE' and not recipe_user:
            raise serializers.ValidationError(
                'Рецепта нет в Корзине.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSmallSerializer(instance.recipe, context=context).data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSmallSerializer(
            recipes, many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        model = Follower
        fields = ('user', 'author')

    def validate(self, data):
        method = self.context.get('method')
        user = data['user']
        author = data['author']
        if method == 'POST' and user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        user_author = Follower.objects.filter(
            user=user, author=author
        ).exists()
        if method == 'POST' and user_author:
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        if method == 'DELETE' and not user_author:
            raise serializers.ValidationError(
                'Вы не подписаны на этого пользователя.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionSerializer(
            instance.author, context={'request': request}
        ).data
