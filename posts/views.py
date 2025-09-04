# posts/views.py
# Views for the 'posts' app.

from django.contrib.auth.mixins import LoginRequiredMixin # For login protection
from django.views.generic import ListView, DetailView, CreateView  # Generic views for list and detail pages
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

class PostCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new Post.
    Requires user to be logged in.
    """
    model = Post
    fields = ["title", "slug", "content"]     # Fields shown in the form
    template_name = "posts/post_form.html"    # Template to render
    context_object_name = "form"

    def form_valid(self, form):
        """
        Override form_valid to automatically assign the logged-in user
        as the author before saving.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        After creating the post, redirect to its detail page.
        """
        return self.object.get_absolute_url()