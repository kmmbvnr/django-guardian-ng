.. _admin-integration:

Admin integration
=================

Django comes with excellent and widely used *Admin* application. Basically,
it provides content management for Django applications. User with access to
admin panel can manage users, groups, permissions and other data provided by
system.

``django-guardian`` comes with simple object permissions management integration
for Django's admin application.

Usage
-----

It is very easy to use admin integration. Simply use :admin:`GuardedModelAdmin`
instead of standard ``django.contrib.admin.ModelAdmin`` class for registering
models within the admin. In example, look at following model:

.. code-block:: python

    from django.db import models


    class Post(models.Model):
        title = models.CharField('title', max_length=64)
        slug = models.SlugField(max_length=64)
        content = models.TextField('content')
        created_at = models.DateTimeField(auto_now_add=True, db_index=True)

        class Meta:
            permissions = (
                ('hide_post', 'Can hide post'),
            )
            get_latest_by = 'created_at'

        def __str__(self):
            return self.title

        def get_absolute_url(self):
            return {'post_slug': self.slug}

We want to register ``Post`` model within admin application. Normally, we would
do this as follows within ``admin.py`` file of our application:

.. code-block:: python

    from django.contrib import admin

    from posts.models import Post


    class PostAdmin(admin.ModelAdmin):
        prepopulated_fields = {"slug": ("title",)}
        list_display = ('title', 'slug', 'created_at')
        search_fields = ('title', 'content')
        ordering = ('-created_at',)
        date_hierarchy = 'created_at'

    admin.site.register(Post, PostAdmin)


If we would like to add object permissions management for ``Post`` model we
would need to change ``PostAdmin`` base class into ``GuardedModelAdmin``.
Our code could look as follows:

.. code-block:: python

    from django.contrib import admin

    from posts.models import Post

    from guardian.admin import GuardedModelAdmin


    class PostAdmin(GuardedModelAdmin):
        prepopulated_fields = {"slug": ("title",)}
        list_display = ('title', 'slug', 'created_at')
        search_fields = ('title', 'content')
        ordering = ('-created_at',)
        date_hierarchy = 'created_at'

    admin.site.register(Post, PostAdmin)

And thats it. We can now navigate to **change** post page and just next to the
*history* link we can click *Object permissions* button to manage row level
permissions.

.. note::
   Example above is shipped with ``django-guardian`` package with the example
   project.


Restrict Admin Object Access
----------------------------

GuardedModelAdmin does not introduce object-level permissions for the Admin site
by default. If you need to restrict access based on django-guardian permissions,
you need to override additional methods in the Django Admin:

    class PostAdmin(GuardedModelAdmin):
        ...

        def get_queryset(self, request):
            queryset = super().get_queryset(request)
            codename = get_permission_codename("view", self.opts)
            return get_objects_for_user(request.user, f"{self.opts.app_label}.{codename}")

        def has_delete_permission(self, request, obj=None):
            permitted = super().has_delete_permission(request, obj=boj)
            if not permitted and obj:
                codename = get_permission_codename("delete", self.opts)
                permitted = request.user.has_perm(f"{self.opts.app_label}.{codename}")
            return permitted

        def has_view_permission(self, request, obj=None):
            permitted = super().has_delete_permission(request, obj=boj)
            if not permitted and obj:
                codename = get_permission_codename("view", self.opts)
                permitted = request.user.has_perm(f"{self.opts.app_label}.{codename}")
            return permitted

        def has_change_permission(self, request, obj=None):
            permitted = super().has_change_permission(request, obj=boj)
            if not permitted and obj:
                codename = get_permission_codename("change", self.opts)
                permitted = request.user.has_perm(f"{self.opts.app_label}.{codename}")
            return permitted
