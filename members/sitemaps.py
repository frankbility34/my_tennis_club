from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post, Category, Tag


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status="published").order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("post_detail", args=[obj.id])


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all().order_by("category_name")

    def location(self, obj):
        return reverse("category_posts", args=[obj.id])


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Tag.objects.all().order_by("tg_name")

    def location(self, obj):
        return reverse("tag_posts", args=[obj.slug])


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            "home",
            "about",
            "contact",
        ]

    def location(self, item):
        return reverse(item)