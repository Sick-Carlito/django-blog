# posts/views.py
# Views for the 'posts' app.

from django.views.generic import ListView, DetailView,CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from .models import Post


class PostListView(ListView):
    """
    Displays a paginated list of Post objects (newest first via model Meta.ordering).
    """
    model = Post                                   # model to query
    template_name = "posts/post_list.html"         # template to render
    context_object_name = "posts"                  # context variable for template
    paginate_by = 10                               # pagination size


class PostDetailView(DetailView):
    """
    Displays a single Post identified by its slug.
    """
    model = Post                                   # model to query
    template_name = "posts/post_detail.html"       # template to render
    context_object_name = "post"                   # name used in template context
    slug_field = "slug"                            # model field used for lookup
    slug_url_kwarg = "slug"                        # URL kwarg providing the slug


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Admin-only view to create a new Post.
    - LoginRequiredMixin forces anonymous users to log in first (302 to LOGIN_URL).
    - UserPassesTestMixin with test_func ensures only staff users pass (else 403).
    """
    model = Post                                   # model to create
    fields = ["title", "slug", "content"]          # form fields to expose
    template_name = "posts/post_form.html"         # template used to render the form
    context_object_name = "form"                   # ensure 'form' key exists in context for tests

    # If the user is authenticated but fails test_func, raise 403 instead of redirect
    raise_exception = True                         # return HTTP 403 for logged-in users who fail the test

    def test_func(self):
        """
        Only allow staff/admin users.
        Returns True if the current user is staff; False otherwise.
        """
        user = self.request.user                   # the current user from the request
        return user.is_staff                       # True for staff/admin accounts
    
    def handle_no_permission(self):
        """
        Handle permission denied. Redirect anonymous users to login,
        return 403 for authenticated non-staff users.
        """
        if not self.request.user.is_authenticated:
            # Anonymous user - redirect to login
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name()
            )
        else:
            # Authenticated but failed test_func - return 403
            return HttpResponseForbidden()

    def form_valid(self, form):
        """
        Before saving, attach the current user as the post author.
        """
        form.instance.author = self.request.user   # set the author to the logged-in staff user
        return super().form_valid(form)            # proceed with default save behavior

    def get_success_url(self):
        """
        After creation, redirect to the new post's detail page.
        """
        return self.object.get_absolute_url()      # use Post.get_absolute_url()
