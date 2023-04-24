from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers

from .fields import Base64ImageField
from recipes.models import (
    FavoriteRecipe, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import CustomUser, Follow


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author=obj,
            user=user
        ).exists()


class IgredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True,
        source='ingredient'
    )
    name = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        source='ingredient'
    )
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit',
        read_only=True,
        source='ingredient'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IgredientRecipeSerializer(
        read_only=True, many=True,
        source='ingredients_recipe'
    )
    image = Base64ImageField(use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            recipe=obj,
            user=user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=user
        ).exists()


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate_name(self, name):
        if self.context.get('request').method == 'POST':
            if Recipe.objects.filter(
                author=self.context.get('request').user,
                name=self.initial_data.get('name')
            ).exists():
                raise exceptions.ValidationError(
                    'Вы уже публиковали рецепт с таким названием'
                )
        return name

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise exceptions.ValidationError(
                'У рецепта должны быть ингредиенты'
            )
        current_ingredients = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(current_ingredients) != len(set(current_ingredients)):
            raise exceptions.ValidationError(
                'Вы уже добавили этот ингредиент'
            )
        current_amounts = [
            ingredient.get('amount') for ingredient in ingredients
        ]
        for amount in current_amounts:
            if amount <= 0:
                raise exceptions.ValidationError(
                    'Укажите количество ингредиентов'
                )
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ])

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        new_recipe = Recipe.objects.create(**validated_data)
        new_recipe.tags.set(tags_data)
        self.create_ingredients(
            ingredients=ingredients_data, recipe=new_recipe
        )
        return new_recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author=obj.author,
            user=obj.user
        ).exists()

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit:
            recipes = recipes[:int(limit)]
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
