from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import os
import resend
from django.core.mail import send_mail, get_connection
from django.contrib import messages
from .models import Post, Category, Tag, Comment, Media
from django.shortcuts import render
from django.db import connection
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode





# Create your views here.









def Myhome(request):

    # =========================================================
    # ALL PUBLISHED POSTS
    # =========================================================

    published_posts = (
        Post.objects
        .filter(status="published")
        .select_related(
            "author",
            "category",
            "featured_image"
        )
        .prefetch_related("tags")
        .order_by("-created_at")
    )


    # =========================================================
    # LATEST POSTS
    # =========================================================
    # The 6 most recently published posts.

    latest_posts = published_posts[:6]


    # =========================================================
    # TOP POSTS
    # =========================================================
    # Posts with the most comments.
    #
    # -comment_count = highest comments first
    # -created_at = newest first if comments are equal

    top_posts = (
        Post.objects
        .filter(status="published")
        .select_related(
            "author",
            "category",
            "featured_image"
        )
        .prefetch_related("tags")
        .annotate(
            comment_count=Count("comments")
        )
        .order_by(
            "-comment_count",
            "-created_at"
        )[:5]
    )


    # =========================================================
    # CATEGORIES
    # =========================================================

    categories = (
        Category.objects
        .all()
        .order_by("category_name")
    )


    # =========================================================
    # TAGS
    # =========================================================

    tags = (
        Tag.objects
        .all()
        .order_by("tg_name")
    )


    # =========================================================
    # POSTS FOR EACH CATEGORY
    # =========================================================
    # Every category gets its own latest 4 published posts.
    #
    # Example:
    #
    # Sports
    #   → Post 1
    #   → Post 2
    #   → Post 3
    #
    # Technology
    #   → Post 1
    #   → Post 2
    #
    # Business
    #   → Post 1
    #
    # etc.
    # =========================================================

    category_sections = []

    for category in categories:

        posts = (
            Post.objects
            .filter(
                status="published",
                category=category
            )
            .select_related(
                "author",
                "category",
                "featured_image"
            )
            .prefetch_related("tags")
            .order_by("-created_at")[:4]
        )

        # Only show a category section if
        # the category actually contains published posts.

        if posts:

            category_sections.append({
                "category": category,
                "posts": posts
            })


    # =========================================================
    # CONTEXT
    # =========================================================

    context = {

        "latest_posts": latest_posts,

        "top_posts": top_posts,

        "categories": categories,

        "tags": tags,

        "category_sections": category_sections,
    }


    # =========================================================
    # RENDER HOME PAGE
    # =========================================================

    return render(
        request,
        "index.html",
        context
    )


def robots_txt(request):

    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "Sitemap: https://www.msannewsblog.com/sitemap.xml\n"
    )

    return HttpResponse(
        content,
        content_type="text/plain"
    )







    

def categories(request):

    categories = Category.objects.all()

    return render(
        request,
        "categories.html",
        {"categories": categories}
    )


@staff_member_required
def category_management(request):
    categories = Category.objects.all()

    return render(request, "category_management.html", {
        "categories": categories
    })   


@staff_member_required
def create_category(request):

    if request.method == "POST":

        category_name = request.POST["category_name"]

        if category_name:
            Category.objects.create(
                category_name=category_name
            )

        return redirect("categories")

    return redirect("categories")

@staff_member_required
def edit_category(request, category_id):

    category = Category.objects.get(id=category_id)

    if request.method == "POST":

        category_name = request.POST["category_name"]

        if category_name:
            category.category_name = category_name
            category.save()

        return redirect("categories")

    return render(
        request,
        "edit_category.html",
        {"category": category}
    )

@staff_member_required
def delete_category(request, category_id):

    category = Category.objects.get(id=category_id)

    category.delete()

    return redirect("categories")


@staff_member_required
def tags_management(request):

    tags = Tag.objects.all()

    context = {
        "tags": tags
    }

    return render(
        request,
        "tags_management.html",
        context
    )

@staff_member_required
def add_tag(request):

    if request.method == "POST":

        tg_name = request.POST.get("tg_name", "").strip()

        if not tg_name:
            messages.error(
                request,
                "Tag name cannot be empty."
            )

            return redirect("tags_management")

        if Tag.objects.filter(tg_name__iexact=tg_name).exists():

            messages.error(
                request,
                "This tag already exists."
            )

            return redirect("tags_management")

        Tag.objects.create(
            tg_name=tg_name
        )

        messages.success(
            request,
            "Tag added successfully."
        )

    return redirect("tags_management")


@staff_member_required
def edit_tag(request, tag_id):

    tag = get_object_or_404(
        Tag,
        id=tag_id
    )

    if request.method == "POST":

        tg_name = request.POST.get("tg_name", "").strip()

        if not tg_name:

            messages.error(
                request,
                "Tag name cannot be empty."
            )

            return redirect(
                "edit_tag",
                tag_id=tag.id
            )

        if Tag.objects.filter(
            tg_name__iexact=tg_name
        ).exclude(id=tag.id).exists():

            messages.error(
                request,
                "A tag with this name already exists."
            )

            return redirect(
                "edit_tag",
                tag_id=tag.id
            )

        tag.tg_name = tg_name

        
        tag.slug = ""

        tag.save()

        messages.success(
            request,
            "Tag updated successfully."
        )

        return redirect("tags_management")

    context = {
        "tag": tag
    }

    return render(
        request,
        "edit_tag.html",
        context
    )

@staff_member_required
def delete_tag(request, tag_id):

    tag = get_object_or_404(
        Tag,
        id=tag_id
    )

    if request.method == "POST":

        tag_name = tag.tg_name

        tag.delete()

        messages.success(
            request,
            f'Tag "{tag_name}" was deleted successfully.'
        )

    return redirect("tags_management")



@staff_member_required
def authors(request):

    users = User.objects.all()

    return render(request, "authors.html", {
        "users": users
    })    

@staff_member_required
def create_author(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        # Check if username already exists
        if User.objects.filter(username=username).exists():

            messages.warning(
                request,
                f"Username '{username}' already exists. Please choose another username."
            )

            return redirect("create_author")

        # Create the author
        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(
            request,
            f"Author '{username}' was created successfully."
        )

        return redirect("authors")

    return render(
        request,
        "create_author.html"
    )


@staff_member_required
def edit_author(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        user.first_name = request.POST["first_name"]
        user.last_name = request.POST["last_name"]
        user.username = request.POST["username"]
        user.email = request.POST["email"]

        user.save()

        messages.success(
            request,
            "Author updated successfully."
        )

        return redirect("authors")

    return render(
        request,
        "edit_author.html",
        {
            "user": user
        }
    )

@staff_member_required
def delete_author(request, user_id):

    user = User.objects.get(id=user_id)

    user.delete()

    messages.success(
        request,
        "Author deleted successfully."
    )

    return redirect("authors") 


@staff_member_required
def posts(request):

    posts = Post.objects.all().order_by("-created_at")

    return render(
        request,
        "posts.html",
        {
            "posts": posts
        }
    )      

@staff_member_required
def create_post(request):

    # =========================================================
    # POST REQUEST
    # This runs when the user submits the Create Post form.
    # =========================================================

    if request.method == "POST":

        title = request.POST.get("title")
        author_id = request.POST.get("author")
        category_id = request.POST.get("category")
        excerpt = request.POST.get("excerpt")
        content = request.POST.get("content")
        status = request.POST.get("status")
        media_id = request.POST.get("featured_image")


        # =====================================================
        # CATEGORY
        # =====================================================

        category = None

        if category_id:

            category = get_object_or_404(
                Category,
                id=category_id
            )


        # =====================================================
        # FEATURED IMAGE
        # Get the image from the Media Library.
        # =====================================================

        featured_image = None

        if media_id:

            featured_image = get_object_or_404(
                Media,
                id=media_id
            )


        # =====================================================
        # AUTHOR
        # =====================================================

        author = get_object_or_404(
            User,
            id=author_id
        )


        # =====================================================
        # CREATE POST
        # =====================================================

        post = Post.objects.create(
            title=title,
            author=author,
            category=category,
            excerpt=excerpt,
            content=content,
            featured_image=featured_image,
            status=status
        )


        # =====================================================
        # TAGS
        # =====================================================

        tag_ids = request.POST.getlist("tags")

        post.tags.set(tag_ids)


        # =====================================================
        # SUCCESS MESSAGE
        # =====================================================

        messages.success(
            request,
            "Post created successfully."
        )


        # =====================================================
        # RETURN TO POST MANAGEMENT
        # =====================================================

        return redirect("posts")


    # =========================================================
    # GET REQUEST
    # This runs when the user clicks:
    # "+ Create New Post"
    # =========================================================

    authors = User.objects.all()

    categories = Category.objects.all()

    tags = Tag.objects.all()

    media = Media.objects.all()


    # =========================================================
    # SEND DATA TO CREATE_POST.HTML
    # =========================================================

    context = {
        "authors": authors,
        "categories": categories,
        "tags": tags,
        "media": media,
    }


    return render(
        request,
        "create_post.html",
        context
    )



@staff_member_required
def edit_post(request, post_id):

    post = Post.objects.get(id=post_id)

    if request.method == "POST":

        # TITLE
        post.title = request.POST["title"]

        # AUTHOR
        author_id = request.POST.get("author")

        if author_id:
            post.author = User.objects.get(
                id=author_id
            )

        # CATEGORY
        category_id = request.POST.get("category")

        if category_id:
            post.category = Category.objects.get(
                id=category_id
            )

        # EXCERPT
        post.excerpt = request.POST["excerpt"]

        # CONTENT
        post.content = request.POST["content"]

        # STATUS
        post.status = request.POST["status"]

        # FEATURED IMAGE FROM MEDIA LIBRARY
        media_id = request.POST.get("featured_image")

        if media_id:
            post.featured_image = Media.objects.get(
                id=media_id
            )
        else:
            post.featured_image = None

        # SAVE POST
        post.save()

        # TAGS
        tag_ids = request.POST.getlist("tags")

        post.tags.set(tag_ids)

        messages.success(
            request,
            "Post updated successfully."
        )

        return redirect("posts")

    # DATA FOR THE EDIT FORM
    authors = User.objects.all()
    categories = Category.objects.all()
    tags = Tag.objects.all()
    media = Media.objects.all()

    return render(
        request,
        "edit_post.html",
        {
            "post": post,
            "authors": authors,
            "categories": categories,
            "tags": tags,
            "media": media,
        }
    )





@staff_member_required
def delete_post(request, post_id):

    post = Post.objects.get(id=post_id)

    post.delete()

    messages.success(
        request,
        "Post deleted successfully."
    )

    return redirect("posts")  
 
@staff_member_required    
def comments(request):

    comments = Comment.objects.all().order_by("-created_at")
 

    return render(
        request,
        "comments.html",
        {
            "comments": comments
        }
    )  










@login_required
def create_comment(request, post_id):

    # =========================================================
    # ONLY ACCEPT POST REQUESTS
    # =========================================================

    if request.method != "POST":
        return redirect(
            "post_detail",
            post_id=post_id
        )

    # =========================================================
    # GET COMMENT CONTENT
    # =========================================================

    content = request.POST.get(
        "content",
        ""
    ).strip()

    if not content:
        messages.error(
            request,
            "Comment cannot be empty."
        )

        return redirect(
            "post_detail",
            post_id=post_id
        )

    # =========================================================
    # GET PUBLISHED POST
    # =========================================================

    post = get_object_or_404(
        Post,
        id=post_id,
        status="published"
    )

    # =========================================================
    # CREATE COMMENT
    # =========================================================

    comment = Comment.objects.create(
        post=post,
        user=request.user,
        content=content
    )

    # =========================================================
    # DATABASE DEBUG INFORMATION
    # =========================================================

    print("======================================")
    print("COMMENT CREATED")
    print("COMMENT ID:", comment.id)
    print("COMMENT USER:", comment.user.username)
    print("COMMENT STATUS:", comment.status)
    print(
        "TOTAL COMMENTS NOW:",
        Comment.objects.count()
    )
    print("DATABASE: PostgreSQL")
    print("======================================")

    # =========================================================
    # SEND EMAIL USING RESEND
    # =========================================================

    try:

        resend.api_key = settings.RESEND_API_KEY

        params = {
            "from": settings.DEFAULT_FROM_EMAIL,

            "to": [
                settings.ADMIN_EMAIL
            ],

            "subject": (
                "New Comment Awaiting Approval - "
                f"{post.title}"
            ),

            "html": f"""
                <h2>New Comment Awaiting Approval</h2>

                <p>
                    A new comment has been submitted
                    to MSAN News Blog.
                </p>

                <hr>

                <p>
                    <strong>Post:</strong>
                    {post.title}
                </p>

                <p>
                    <strong>Author:</strong>
                    {request.user.get_username()}
                </p>

                <p>
                    <strong>Email:</strong>
                    {request.user.email}
                </p>

                <p>
                    <strong>Comment:</strong>
                </p>

                <blockquote>
                    {content}
                </blockquote>

                <hr>

                <p>
                    <strong>Status:</strong>
                    Pending approval
                </p>

                <p>
                    Please log in to the comment management
                    area to approve or reject this comment.
                </p>
            """
        }

        email = resend.Emails.send(params)

        print("======================================")
        print("COMMENT EMAIL: SENT SUCCESSFULLY")
        print("RESEND RESPONSE:", email)
        print("======================================")

    except Exception as e:

        # =====================================================
        # EMAIL FAILURE MUST NOT DELETE THE COMMENT
        # =====================================================

        print("======================================")
        print(
            "COMMENT EMAIL ERROR:",
            repr(e)
        )
        print("======================================")

    # =========================================================
    # ALWAYS RETURN SUCCESS TO USER
    # =========================================================

    messages.success(
        request,
        "Your comment has been submitted for review."
    )

    return redirect(
        "post_detail",
        post_id=post.id
    )





@staff_member_required
def approve_comment(request, comment_id):

    comment = Comment.objects.get(
        id=comment_id
    )

    comment.status = "approved"

    comment.save()

    messages.success(
        request,
        "Comment approved successfully."
    )

    return redirect("comments")


@staff_member_required
def reject_comment(request, comment_id):

    comment = Comment.objects.get(
        id=comment_id
    )

    comment.status = "rejected"

    comment.save()

    messages.warning(
        request,
        "Comment rejected."
    )

    return redirect("comments")

@staff_member_required
def delete_comment(request, comment_id):

    comment = Comment.objects.get(
        id=comment_id
    )

    comment.delete()

    messages.success(
        request,
        "Comment deleted successfully."
    )

    return redirect("comments")    



@staff_member_required
def media_management(request):

    search = request.GET.get(
        "search",
        ""
    )

    # Only include Media records that actually have an image file.
    media = Media.objects.exclude(
        image=""
    ).exclude(
        image__isnull=True
    )

    if search:

        media = media.filter(
            title__icontains=search
        )

    media = media.order_by(
        "-created_at"
    )

    return render(
        request,
        "media_management.html",
        {
            "media": media,
            "search": search
        }
    )




@staff_member_required
def upload_media(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        image = request.FILES.get(
            "image"
        )

        # Check that a title was provided
        if not title:

            messages.error(
                request,
                "Please enter an image title."
            )

            return redirect(
                "upload_media"
            )

        # Check that an image was actually selected
        if not image:

            messages.error(
                request,
                "Please choose an image before uploading."
            )

            return redirect(
                "upload_media"
            )

        # Create the Media record
        Media.objects.create(
            title=title,
            image=image,
            uploaded_by=request.user
        )

        messages.success(
            request,
            "Image uploaded successfully."
        )

        return redirect(
            "media_management"
        )

    return render(
        request,
        "upload_media.html"
    )


@staff_member_required
def delete_media(request, media_id):

    media = Media.objects.get(
        id=media_id
    )

    if media.image:
        media.image.delete(save=False)

    media.delete()

    messages.success(
        request,
        "Media deleted successfully."
    )

    return redirect("media_management") 

@staff_member_required
def database_check(request):

    from django.db import connection

    return HttpResponse(
        f"Database: {connection.vendor}<br>"
        f"Users: {User.objects.count()}<br>"
        f"Posts: {Post.objects.count()}<br>"
        f"Comments: {Comment.objects.count()}<br>"
        f"Categories: {Category.objects.count()}<br>"
        f"Tags: {Tag.objects.count()}<br>"
        f"Media: {Media.objects.count()}"
    )


@staff_member_required 
def dashboard(request):

    total_posts = Post.objects.count()

    total_authors = User.objects.count()

    total_comments = Comment.objects.count()

    total_media = Media.objects.count()

    total_categories = Category.objects.count()

    total_tags = Tag.objects.count()

    published_posts = Post.objects.filter(
        status="published"
    ).count()

    draft_posts = Post.objects.filter(
        status="draft"
    ).count()

    approved_comments = Comment.objects.filter(
        status="approved"
    ).count()

    pending_comments = Comment.objects.filter(
        status="pending"
    ).count()

    rejected_comments = Comment.objects.filter(
        status="rejected"
    ).count()

    recent_posts = Post.objects.all().order_by(
        "-created_at"
    )[:5]

    recent_comments = Comment.objects.all().order_by(
        "-created_at"
    )[:5]
    
    popular_posts = Post.objects.annotate(
        comment_count=Count("comments")
    ).order_by(
        "-comment_count"
    )[:5] 

    context = {
        "total_posts": total_posts,
        "total_authors": total_authors,
        "total_comments": total_comments,
        "total_media": total_media,
        "total_categories": total_categories,
        "total_tags": total_tags,
        "published_posts": published_posts,
        "draft_posts": draft_posts,
        "approved_comments": approved_comments,
        "pending_comments": pending_comments,
        "rejected_comments": rejected_comments,
        "recent_posts": recent_posts,
        "recent_comments": recent_comments,
        "popular_posts": popular_posts,
    }

    return render(
        request,
        "dashboard.html",
        context
    )  




# =========================================================
# SEARCH
# =========================================================

def search(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    # =========================================================
    # GET PUBLISHED POSTS
    # =========================================================

    posts = (
        Post.objects
        .filter(
            status="published"
        )
        .select_related(
            "author",
            "category",
            "featured_image"
        )
        .prefetch_related(
            "tags"
        )
        .order_by(
            "-created_at"
        )
    )

    # =========================================================
    # SEARCH
    # =========================================================

    if query:

        posts = posts.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(category__category_name__icontains=query)
            | Q(tags__tg_name__icontains=query)
        ).distinct()

    # =========================================================
    # PAGINATION
    # =========================================================

    paginator = Paginator(
        posts,
        6
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    # =========================================================
    # CONTEXT
    # =========================================================

    context = {
        "query": query,
        "posts": page_obj,
        "page_obj": page_obj,
    }

    # =========================================================
    # RENDER SEARCH PAGE
    # =========================================================

    return render(
        request,
        "search.html",
        context
    )






def post_detail(request, post_id):

    post = get_object_or_404(
        Post.objects.select_related(
            "featured_image",
            "category",
            "author"
        ).prefetch_related(
            "tags"
        ),
        id=post_id,
        status="published"
    )

    comments = post.comments.filter(
        status="approved"
    ).select_related(
        "user"
    ).order_by(
        "-created_at"
    )

    # Get all categories for the sidebar
    categories = Category.objects.all().order_by(
        "category_name"
    )

    # Get all tags for the sidebar
    tags = Tag.objects.all().order_by(
        "tg_name"
    )

    context = {
        "post": post,
        "comments": comments,
        "categories": categories,
        "tags": tags,
    }

    return render(
        request,
        "post_detail.html",
        context
    )











# =========================================================
# CATEGORY POSTS
# =========================================================

def category_posts(request, category_id):

    # =========================================================
    # GET CATEGORY
    # =========================================================

    category = get_object_or_404(
        Category,
        id=category_id
    )

    # =========================================================
    # GET PUBLISHED POSTS FOR THIS CATEGORY
    # =========================================================

    posts = (
        Post.objects
        .filter(
            category=category,
            status="published"
        )
        .select_related(
            "author",
            "category",
            "featured_image"
        )
        .prefetch_related(
            "tags"
        )
        .order_by(
            "-created_at"
        )
    )

    # =========================================================
    # PAGINATION
    # =========================================================

    paginator = Paginator(
        posts,
        6
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    # =========================================================
    # CONTEXT
    # =========================================================

    context = {
        "category": category,
        "posts": page_obj,
        "page_obj": page_obj,
    }

    # =========================================================
    # RENDER CATEGORY PAGE
    # =========================================================

    return render(
        request,
        "category_posts.html",
        context
    )




def tag_posts(request, slug):

    tag = get_object_or_404(
        Tag,
        slug=slug
    )

    posts = (
        Post.objects
        .filter(
            tags=tag,
            status="published"
        )
        .select_related(
            "author",
            "category",
            "featured_image"
        )
        .prefetch_related(
            "tags"
        )
        .order_by(
            "-created_at"
        )
    )

    paginator = Paginator(
        posts,
        6
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "tag": tag,
        "posts": page_obj,
        "page_obj": page_obj,
    }

    return render(
        request,
        "tag_posts.html",
        context
    )





def author_posts(request, user_id):
    author = get_object_or_404(
        User,
        id=user_id
    )

    posts = (
        Post.objects
        .filter(
            author=author,
            status="published"
        )
        .select_related(
            "author",
            "category",
            "featured_image"
        )
        .prefetch_related(
            "tags"
        )
        .order_by(
            "-created_at"
        )
    )

    paginator = Paginator(
        posts,
        6
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "author": author,
        "posts": page_obj,
        "page_obj": page_obj,
    }

    return render(
        request,
        "author_posts.html",
        context
    )










def register(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check required fields

        if not first_name or not last_name or not username or not email or not password:

            messages.error(
                request,
                "All fields are required."
            )

            return redirect("register")


        # Check username

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")


        # Check email

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "An account with this email already exists."
            )

            return redirect("register")


        # Check passwords

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")


        # Create inactive user

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )

        user.is_active = False
        user.save()


        # Create secure verification token

        signer = TimestampSigner()

        token = signer.sign(user.pk)


        # Build verification URL


        verification_url = (
            f"{settings.SITE_URL}/verify-email/{token}/"
        )


        # Configure Resend

        resend.api_key = settings.RESEND_API_KEY


        # Send verification email

        resend.Emails.send({
            "from": "info@msannewsblog.com",
            "to": [user.email],
            "subject": "Verify Your My Blog Account",
            "html": f"""
                <h2>Welcome to My Blog, {user.first_name}!</h2>

                <p>
                    Thank you for creating an account with us.
                </p>

                <p>
                    Please verify your email address by clicking
                    the button below:
                </p>

                <p>
                    <a
                        href="{verification_url}"
                        style="
                            display:inline-block;
                            padding:12px 20px;
                            background:#007bff;
                            color:white;
                            text-decoration:none;
                            border-radius:5px;
                        "
                    >
                        Verify My Email
                    </a>
                </p>

                <p>
                    If you did not create this account, you can
                    safely ignore this email.
                </p>
            """
        })


        messages.success(
            request,
            "Your account was created. Please check your email and click the verification link before logging in."
        )

        return redirect("login")


    return render(
        request,
        "register.html"
    )



def verify_email(request, token):

    signer = TimestampSigner()

    try:

        user_id = signer.unsign(
            token,
            max_age=60 * 60 * 24
        )

    except SignatureExpired:

        messages.error(
            request,
            "This verification link has expired. Please register again."
        )

        return redirect("register")

    except BadSignature:

        messages.error(
            request,
            "This verification link is invalid."
        )

        return redirect("register")


    try:

        user = User.objects.get(
            pk=user_id
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "The user account could not be found."
        )

        return redirect("register")


    if user.is_active:

        messages.info(
            request,
            "Your email address has already been verified."
        )

        return redirect("login")


    user.is_active = True
    user.save()


    messages.success(
        request,
        "Your email has been verified successfully. You can now log in."
    )

    return redirect("login")







def user_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )


        user = authenticate(
            request,
            username=username,
            password=password
        )


        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                "You have successfully logged in."
            )

            return redirect("home")


        # Check whether the username belongs to an
        # inactive account

        try:

            existing_user = User.objects.get(
                username__iexact=username
            )

            if not existing_user.is_active:

                messages.error(
                    request,
                    "Please verify your email address before logging in."
                )

                return redirect("login")

        except User.DoesNotExist:

            pass


        messages.error(
            request,
            "Invalid username or password."
        )

        return redirect("login")


    return render(
        request,
        "login.html"
    )





def password_reset_request(request):

    if request.method == "POST":

        form = PasswordResetForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"].strip()

            print(
                "PASSWORD RESET REQUEST FOR:",
                email
            )

            # =====================================================
            # GET RESEND API KEY
            # =====================================================

            api_key = settings.RESEND_API_KEY

            print(
                "RESEND API KEY FOUND:",
                bool(api_key)
            )

            if not api_key:

                print(
                    "ERROR: RESEND_API_KEY is not configured."
                )

                messages.error(
                    request,
                    "We could not send the password reset email. Please try again later."
                )

                return redirect(
                    "password_reset"
                )

            resend.api_key = api_key

            # =====================================================
            # FIND USER
            # =====================================================

            users = User.objects.filter(
                email__iexact=email
            )

            if not users.exists():

                print(
                    "NO USER FOUND FOR:",
                    email
                )

                # For security, do not reveal whether an
                # email address exists in the database.

                messages.success(
                    request,
                    "If an account with that email exists, password reset instructions have been sent."
                )

                return redirect(
                    "password_reset_done"
                )

            # =====================================================
            # PROCESS USER
            # =====================================================

            email_sent = False

            for user in users:

                # =================================================
                # CREATE SECURE DJANGO PASSWORD RESET TOKEN
                # =================================================

                uid = urlsafe_base64_encode(
                    force_bytes(user.pk)
                )

                token = default_token_generator.make_token(
                    user
                )

                # =================================================
                # CREATE RESET URL
                # =================================================

                reset_path = reverse(
                    "password_reset_confirm",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    }
                )

                reset_url = (
                    f"{settings.SITE_URL}{reset_path}"
                )

                print(
                    "PASSWORD RESET URL:",
                    reset_url
                )

                # =================================================
                # EMAIL CONTENT
                # =================================================

                subject = (
                    "Password Reset Request - News Blog"
                )

                html_message = f"""
                <!DOCTYPE html>

                <html>

                <head>
                    <meta charset="UTF-8">
                    <title>Password Reset</title>
                </head>

                <body>

                    <h2>Password Reset Request</h2>

                    <p>
                        Hello {user.first_name},
                    </p>

                    <p>
                        We received a request to reset the
                        password for your News Blog account.
                    </p>

                    <p>
                        Click the button below to choose
                        a new password:
                    </p>

                    <p>

                        <a
                            href="{reset_url}"
                            style="
                                display:inline-block;
                                padding:12px 20px;
                                background:#007bff;
                                color:#ffffff;
                                text-decoration:none;
                                border-radius:5px;
                            "
                        >
                            Reset My Password
                        </a>

                    </p>

                    <p>
                        If the button does not work, copy
                        and paste this link into your browser:
                    </p>

                    <p>
                        <a href="{reset_url}">
                            {reset_url}
                        </a>
                    </p>

                    <p>
                        This password reset link is temporary
                        and can only be used once.
                    </p>

                    <p>
                        If you did not request a password
                        reset, you can safely ignore this email.
                    </p>

                    <p>
                        Thank you,<br>
                        News Blog Team
                    </p>

                </body>

                </html>
                """

                # =================================================
                # SEND THROUGH RESEND
                # =================================================

                try:

                    response = resend.Emails.send(
                        {
                            "from": "info@msannewsblog.com",
                            "to": [user.email],
                            "subject": subject,
                            "html": html_message,
                        }
                    )

                    print(
                        "RESEND PASSWORD RESET RESPONSE:",
                        response
                    )

                    print(
                        "PASSWORD RESET EMAIL SENT TO:",
                        user.email
                    )

                    email_sent = True

                except Exception as e:

                    print(
                        "RESEND PASSWORD RESET ERROR:",
                        repr(e)
                    )

            # =====================================================
            # RESULT
            # =====================================================

            if email_sent:

                messages.success(
                    request,
                    "If an account with that email exists, password reset instructions have been sent."
                )

            else:

                messages.error(
                    request,
                    "We could not send the password reset email. Please try again later."
                )

            return redirect(
                "password_reset_done"
            )

    else:

        form = PasswordResetForm()

    return render(
        request,
        "registration/password_reset_form.html",
        {
            "form": form,
        }
    )





def user_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("home")

@login_required
def profile(request):

    user = request.user

    return render(
        request,
        "profile.html",
        {
            "user": user
        }
    )

@login_required
def edit_profile(request):

    user = request.user

    if request.method == "POST":

        user.first_name = request.POST["first_name"]

        user.last_name = request.POST["last_name"]

        user.email = request.POST["email"]

        user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "edit_profile.html",
        {
            "user": user
        }
    )


def about(request):
    return render(
        request,
        "about.html"
    )





def contact(request):

    if request.method == "POST":

        # =====================================================
        # GET FORM DATA
        # =====================================================

        name = request.POST.get(
            "name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        message = request.POST.get(
            "message",
            ""
        ).strip()


        # =====================================================
        # VALIDATE FORM
        # =====================================================

        if not name or not email or not message:

            messages.error(
                request,
                "Please complete all fields before sending your message."
            )

            return render(
                request,
                "contact.html"
            )


        # =====================================================
        # CHECK RESEND API KEY
        # =====================================================

        api_key = settings.RESEND_API_KEY

        if not api_key:

            print(
                "CONTACT EMAIL ERROR: RESEND_API_KEY is not configured."
            )

            messages.error(
                request,
                "Sorry, your message could not be sent. Please try again later."
            )

            return redirect("contact")


        # =====================================================
        # CONFIGURE RESEND
        # =====================================================

        resend.api_key = api_key


        # =====================================================
        # SEND CONTACT EMAIL
        # =====================================================

        try:

            response = resend.Emails.send(
                {
                    "from": settings.DEFAULT_FROM_EMAIL,

                    "to": [
                        settings.ADMIN_EMAIL
                    ],

                    "reply_to": email,

                    "subject": (
                        f"New Contact Message from {name}"
                    ),

                    "html": f"""
                        <!DOCTYPE html>

                        <html>

                        <head>
                            <meta charset="UTF-8">
                            <title>New Contact Message</title>
                        </head>

                        <body>

                            <h2>
                                New Contact Message
                            </h2>

                            <p>
                                Someone has submitted a message
                                through the MSAN News Blog Contact Us form.
                            </p>

                            <hr>

                            <p>
                                <strong>Name:</strong>
                                {name}
                            </p>

                            <p>
                                <strong>Email:</strong>
                                {email}
                            </p>

                            <hr>

                            <p>
                                <strong>Message:</strong>
                            </p>

                            <p>
                                {message}
                            </p>

                            <hr>

                            <p>
                                MSAN News Blog
                            </p>

                        </body>

                        </html>
                    """
                }
            )


            # =================================================
            # EMAIL SENT SUCCESSFULLY
            # =================================================

            print(
                "CONTACT EMAIL SENT SUCCESSFULLY:"
            )

            print(
                response
            )


            messages.success(
                request,
                "Your message has been sent successfully. "
                "We will get back to you soon."
            )


        # =====================================================
        # EMAIL ERROR
        # =====================================================

        except Exception as e:

            print(
                "======================================"
            )

            print(
                "CONTACT EMAIL ERROR:"
            )

            print(
                repr(e)
            )

            print(
                "======================================"
            )


            messages.error(
                request,
                "Sorry, your message could not be sent. "
                "Please try again later."
            )


        return redirect(
            "contact"
        )


    # =========================================================
    # GET REQUEST
    # =========================================================

    return render(
        request,
        "contact.html"
    )


    



            





