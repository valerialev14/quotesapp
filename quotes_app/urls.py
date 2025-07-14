from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('add/', views.QuoteCreateView.as_view(), name='add_quote'),
    path('like-dislike/', views.LikeDislikeView.as_view(), name='like_dislike'),
    path('top-quotes/', views.TopQuotesView.as_view(), name='top_quotes'),
    path('worst-quotes/', views.WorstQuotesView.as_view(), name='worst_quotes'),
    path('delete-quote/', views.DeleteQuoteView.as_view(), name='delete_quote'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('delete/<int:quote_id>/', views.delete_quote, name='delete_quote'),
]
