from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='home-page'),
    path('lines-intersection/', views.linesIntersectionPage,
         name='lines-intersection-page'),
    path('lines-intersection/method-1', views.linesIntersectionMethod1Page,
         name='lines-intersection-method-1-page'),
    path('lines-intersection/method-2', views.linesIntersectionMethod2Page,
         name='lines-intersection-method-2-page'),
    path('convex-hull/', views.convexHullPage, name='convex-hull-page'),
    path('convex-hull-result/', views.convexHullResultPage,
         name='convex-hull-result-page'),
]
