from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path("", views.Myhome, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("contact/", views.contact, name="contact"),
    path("categories/", views.categories, name="categories"),
    path("category-management/", views.category_management, name="category_management"),
    path("categories/create/", views.create_category, name="create_category"),
    path("categories/edit/<int:category_id>/", views.edit_category, name="edit_category"),
    path("categories/delete/<int:category_id>/", views.delete_category, name="delete_category"),
    path("tags/", views.tags_management, name="tags_management"),
    path("tags/add/", views.add_tag, name="add_tag"),
    path("tags/<int:tag_id>/edit/", views.edit_tag, name="edit_tag"),
    path("tags/<int:tag_id>/delete/", views.delete_tag, name="delete_tag"),
    path("authors/", views.authors, name="authors"),
    path("authors/create/", views.create_author, name="create_author"),
    path("authors/edit/<int:user_id>/", views.edit_author, name="edit_author"),
    path("authors/delete/<int:user_id>/", views.delete_author, name="delete_author"),
    path("posts/", views.posts, name="posts"),
    path("posts/create/", views.create_post, name="create_post"),
    path("posts/edit/<int:post_id>/", views.edit_post, name="edit_post"),
    path("posts/delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path("comments/", views.comments, name="comments"),
    path("posts/<int:post_id>/comment/", views.create_comment, name="create_comment"),
    path("comments/approve/<int:comment_id>/", views.approve_comment, name="approve_comment"),
    path("comments/reject/<int:comment_id>/", views.reject_comment, name="reject_comment"),
    path("comments/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),
    path("media/", views.media_management, name="media_management"),
    path("media/upload/", views.upload_media, name="upload_media"),
    path("media/delete/<int:media_id>/", views.delete_media, name="delete_media"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("search/", views.search,name="search"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("category/<int:category_id>/", views.category_posts, name="category_posts"),
    path("tag/<slug:slug>/", views.tag_posts, name="tag_posts"),
    path("author/<int:user_id>/", views.author_posts, name="author_posts"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
        template_name="password_change.html"
        ),
        name="password_change"
    ),

    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
        template_name="password_change_done.html",
        ),
        name="password_change_done"
    ),

    
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm"
    ),

    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),

    
    
    

        
        
   

    
        
        
        
    

    
        
        
        
    

    
        
        
        
    







]