from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class Member(models.Model):
  firstname = models.CharField(max_length=100)
  lastname = models.CharField(max_length=100)

  class Meta:
    verbose_name_plural = "Member"

  def __str__ (self):
      return f'{self.firstname} {self.lastname}'  
   


class Category(models.Model):

    category_name = models.CharField(
        max_length=100,
        unique=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["category_name"]








class Tag(models.Model):

    tg_name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )

    image = models.ImageField(
        upload_to="tags/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["tg_name"]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.tg_name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.tg_name

 


class Media(models.Model):

    title = models.CharField(
        max_length=200
    )

    image = models.ImageField(
        upload_to="media/"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title                                    


class Post(models.Model):

    title = models.CharField(max_length=200)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True
    )

    excerpt = models.TextField(
        blank=True
    )

    content = models.TextField()

    featured_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.post.title}"


