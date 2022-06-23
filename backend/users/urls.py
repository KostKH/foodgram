from django.urls import include, path

from .views import SubscribeView, SubsriptionsView

urlpatterns = [
    path('users/subscriptions/', SubsriptionsView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(r'users/<int:id>/subscribe/', SubscribeView.as_view()),
]
