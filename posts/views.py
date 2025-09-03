# posts/views.py
# Views for the 'posts' app.

from django.views.generic import ListView, DetailView  # Generic views for list and detail pages
from .models import Post                              # Import Post model to be used by the views


class PostListView(ListView):
    """
    Displays a paginated list of Post objects.
    (Already implemented on Day 8)
    """
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 10


class PostDetailView(DetailView):
    """
    Displays a single Post instance identified by its slug.
    DetailView looks up the object and adds it to the template context.
    """
    model = Post                              # Which model to query
    template_name = "posts/post_detail.html"  # Template to render for the detail view
    context_object_name = "post"              # In template, use 'post' rather than 'object'
    slug_field = "slug"                       # Model field used to look up the object
    slug_url_kwarg = "slug"                   # URL kwarg name expected (e.g., path('<slug:slug>/'))
