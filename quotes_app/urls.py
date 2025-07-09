from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('add/', views.QuoteCreateView.as_view(), name='add_quote'),
    path('like-dislike/', views.LikeDislikeView.as_view(), name='like_dislike'),
    path('top-quotes/', views.TopQuotesView.as_view(), name='top_quotes'),
    path('worst-quotes/', views.WorstQuotesView.as_view(), name='worst_quotes'),
    path('delete-quote/', views.DeleteQuoteView.as_view(), name='delete_quote'),
]