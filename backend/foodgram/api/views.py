from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .filters import AuthorAndTagFilter, IngredientSearchFilter
from .pagination import CustomPagination
from .permissions import AuthorOrReadOnly
from .serializers import (
    CustomUserCreateSerializer, CustomUserSerializer,
    FavoriteRecipeSerializer, FollowSerializer,
    IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, TagSerializer
)
from recipes.models import (
    FavoriteRecipe, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import CustomUser, Follow


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = AuthorAndTagFilter

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST', 'PATCH']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def add_delete_recipe_from_favorite_or_cart(
            self, request, pk, model, recipe_model
        ):
        user = request.user
        recipe = get_object_or_404(recipe_model, id=pk)
        if request.method == 'POST':
            if model.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': f'{recipe.name} уже добавили'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe),
            return Response(
                FavoriteRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not model.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': f'Нет такого рецепта {recipe.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.add_delete_recipe_from_favorite_or_cart(
            request=request, pk=pk, model=FavoriteRecipe,
            recipe_model=Recipe
        )

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_delete_recipe_from_favorite_or_cart(
            request=request, pk=pk, model=ShoppingCart,
            recipe_model=Recipe
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'ingredient_amount'
            )
        pdfmetrics.registerFont(
            TTFont('Slimamif', 'Slimamif.ttf', 'UTF-8')
        )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('Slimamif', size=24)
        page.drawString(200, 800, 'Список ингредиентов')
        page.setFont('Slimamif', size=16)
        height = 750
        for name, amount, unit in ingredients:
            page.drawString(75, height, (f'{name} - {unit}, '
                                         f'{amount}'))
            height -= 25
        page.showPage()
        page.save()
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class CustomUserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                        mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['POST']:
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        ['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        return Response(
            CustomUserSerializer(
                request.user,
                context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(
        ['post'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = get_list_or_404(Follow, user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            context={'request': request},
            many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        ['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Вы не можете подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, author=author).exists():
                return Response({
                    'errors': 'Вы уже подписаны на данного пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                FollowSerializer(
                    Follow.objects.create(user=user, author=author),
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user == author:
                return Response({
                    'errors': 'Вы не можете отписываться от самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                'errors': 'Вы уже отписались'
            }, status=status.HTTP_400_BAD_REQUEST)
