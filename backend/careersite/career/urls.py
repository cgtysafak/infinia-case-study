from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from . import views
from django.urls import path, include

urlpatterns = [
    path('', lambda request: redirect('login'), name='login'),  # Redirect from root URL to login page
    path('home/', views.HomeView.as_view(),  name="home"),
    path('users/', views.UsersView.as_view(), name="users"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('signup/', views.SignUpView.as_view(), name="signup"),
    path('job-list/', views.JobListingsView.as_view(), name="job-list"),
    path('application-list/', views.PastApplicationsView.as_view(), name="application-list"),
    path('past-openings/', views.PastOpeningsView.as_view(), name="past-openings"),
    path('job-detail/<int:job_id>', views.JobDescriptionView.as_view(), name="job-detail"),
    path('candidates/<int:job_id>', views.CandidatesView.as_view(), name="candidates"),
    path('post-list/', views.PostListView.as_view(), name="post-list"),
    path('add-post/', views.AddPostView.as_view(), name="add-post"),
    path('delete-post/<int:post_id>', views.DeletePostView.as_view(), name="delete-post"),
    path('post-detail/<int:post_id>', views.PostDetailView.as_view(), name="post-detail"),
    path('delete-comment/<int:comment_id>', views.DeleteCommentView.as_view(), name="delete-comment"),
    path('delete-job/<int:job_id>', views.DeleteJobView.as_view(), name="delete-job"),
    path('add-job/', views.AddJobView.as_view(), name="add-job"),
    path('edit-job/<int:job_id>', views.EditJobView.as_view(), name="edit-job"),
    path('user/<int:profile_id>', views.ProfileView.as_view(), name="user"),
    path('edit-profile/<int:user_id>', views.ProfileEditView.as_view(), name="edit-profile"),
    path('grading/<int:user_id>', views.GradingView.as_view(), name="grading"),

]
