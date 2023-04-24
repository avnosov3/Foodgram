from django.urls import include, path
from rest_framework import routers

from .views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet,
    TagViewSet
)

router_v1 = routers.DefaultRouter()

router_v1.register(r'users', CustomUserViewSet, basename='users')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')


users_url_patterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(users_url_patterns)),
    # path('', include('djoser.urls'))
]
