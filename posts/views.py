# posts/views.py
# Views for the 'posts' app.

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from .models import Post, Category
from django.shortcuts import get_object_or_404


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
    fields = ["title", "slug", "content", "categories"]          # form fields to expose
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
    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    UpdateView for editing an existing Post.
    Access rules:
      - anonymous users -> redirected to login (LoginRequiredMixin)
      - logged-in users who are NOT the author -> 403 (raise_exception=True)
      - the author (request.user == post.author) can edit the post
    """

    model = Post                                       # which model to update
    fields = ["title", "slug", "content", "categories"]              # fields displayed in the form
    template_name = "posts/post_form.html"             # reuse the create form template
    context_object_name = "form"                       # tests look for 'form' in context
    raise_exception = True                            # return 403 for logged-in users failing test_func

    def test_func(self):
        """
        Return True only if the logged-in user is the author of the post.
        self.get_object() returns the Post instance being edited.
        """
        post = self.get_object()                       # retrieve the Post instance
        return self.request.user == post.author        # True only if same user
    
    def handle_no_permission(self):
        """
        Handle permission denied. Redirect anonymous users to login,
        return 403 for authenticated users who aren't the author.
        """
        if not self.request.user.is_authenticated:
            # Anonymous user - redirect to login
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name()
            )
        else:
            # Authenticated but not the author - return 403
            return HttpResponseForbidden()

    def form_valid(self, form):
        """
        Optionally ensure author isn't changed. We keep author intact.
        """
        form.instance.author = self.get_object().author
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect to the post detail page after a successful update.
        """
        return self.object.get_absolute_url()

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    DeleteView for removing a Post instance.
    Access rules:
      - anonymous -> redirected to login (LoginRequiredMixin)
      - logged-in non-author -> HTTP 403 (raise_exception=True)
      - author -> may delete the post
    """

    model = Post                                      # The model to delete
    template_name = "posts/post_confirm_delete.html"  # Confirmation template
    context_object_name = "post"                      # Template variable name for the object
    success_url = reverse_lazy("posts:post-list")     # Redirect after successful delete
    #raise_exception = True                            # Authenticated users who fail test_func get 403

    def test_func(self):
        """
        Allow only the author to delete the post.
        self.get_object() returns the Post instance being deleted.
        """
        post = self.get_object()
        return self.request.user == post.author
    
    def handle_no_permission(self):
        """
        Handle permission denied. Redirect anonymous users to login,
        return 403 for authenticated non-authors.
        """
        if not self.request.user.is_authenticated:
            # Anonymous user - redirect to login
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name()
            )
        else:
            # Authenticated but not the author - return 403
            return HttpResponseForbidden()
        
class CategoryListView(ListView):
    model = Category
    template_name = 'posts/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'posts/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(categories=self.object)
        return context