# posts/views.py
# Views for the 'posts' app.

from django.views.generic import ListView           # Generic class-based view for listing objects
from .models import Post                            # Import the Post model we want to list


class PostListView(ListView):
    """
    Displays a list of Post objects.
    Uses the template 'posts/post_list.html' and exposes the queryset as 'posts' in the context.
    """
    model = Post                                    # Tells ListView which model to query (Post.objects.all())
    template_name = "posts/post_list.html"          # Explicit template path to render
    context_object_name = "posts"                   # Add 'posts' to context in addition to the default 'object_list'
    paginate_by = 10                                # Optional: paginate results 10 per page (safe to keep now)

    # NOTE: default ordering comes from Post.Meta.ordering = ["-created_at"], so newest is first.
    # If you wanted to enforce here, you could override get_queryset() and order_by('-created_at').
