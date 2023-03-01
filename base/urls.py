from django.urls import path, include
from . import views



urlpatterns= [
    path('login/', views.loginPage, name= 'loginpage'),
    path('logout/', views.logoutPage, name= 'logoutpage'),
    path('register/', views.registerPage, name= 'registerpage'),
    path('updateUser/', views.updateUser, name= 'updateuser'),
    path('', views.home, name = 'home'),
    path('room/<str:pk>/', views.room, name= 'room'),
    path('createRoom/', views.createRoom, name='create_room'),
    path('updateRoom/<str:pk>/', views.updateRoom, name='update_room'),
    path('deletRoom/<str:pk>/', views.deleteRoom, name = 'delete_room'),
    path('deletMessage/<str:pk>/', views.deleteMessage, name = 'delete_Message'),
    path('userprofile/<str:pk>/', views.userProfile, name = 'userprofile'),
    path('mobile_topic/', views.mobile_topic, name= 'mobile_topicpage'),
    path('mobile_activity/', views.mobile_activity, name= 'mobile_activity'),
]