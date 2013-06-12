from django.contrib import admin
from django import http, template
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils.datastructures import SortedDict
from django.views.decorators.cache import never_cache

class ArtcodeAdmin(admin.sites.AdminSite):
    """
    A custom AdminSite that allows apps to be renamed and reordered in the 
    admin index page.  It also allows apps to be hidden from the index and
    for models to be reordered within an app.

    Example:

    admin = ArtcodeAdmin()
    admin.hidden_apps = ['Sites',]  
    admin.index_config = {
        'blog': {
            'label': "My Blog",
            'caption': "Write about stuff...",
            'models': ['Entry', 'Category',], 
            'order': 0
        },
        'auth': {
            'models': ['User',]
            'order': 1
        }
    }
    """
    hidden_apps = []
    index_config = {}

    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            
            if app_label in self.hidden_apps:
                continue
            
            config = {}
            if app_label in self.index_config.keys():
                config = self.index_config[app_label]

            if 'models' in config:
                if model._meta.object_name not in config['models']:
                    continue

            app_title = config.get('label', app_label)
            app_caption = config.get('caption', '')
            hide_links = config.get('hide_links', False)
            order = config.get('order', False)
                
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                        'perms': perms,
                        'order': 0,
                    }
                    if 'models' in config:
                        model_dict['order'] = config['models'].index(model._meta.object_name)

                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'label': app_label,
                            'name': app_title.title(),
                            'caption': app_caption,
                            'app_url': app_label + '/',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                            'ordered': 'order' in config.keys(),
                            'order': order,
                            'hide_links': hide_links
                        }

        ordered_apps = []
        unordered_apps = []
        for app in app_dict.values():
            if app['ordered']:
                ordered_apps.append(app)
            else:
                unordered_apps.append(app)
        
        # Sort ordered apps acording to position in self.ordered_apps list
        ordered_apps.sort(lambda x, y: cmp(x['order'], y['order']))

        # Sort the apps alphabetically.
        unordered_apps.sort(lambda x, y: cmp(x['name'], y['name']))

        app_list = ordered_apps + unordered_apps

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(lambda x, y: cmp(x['name'], y['name']))
            app['models'].sort(lambda x, y: cmp(x['order'], y['order']))

        context = {
            'title': _('Site Administration'),
            'app_list': app_list,
            'root_path': self.root_path,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response(self.index_template or 'admin/index.html', context,
            context_instance=context_instance
        )
    index = never_cache(index)

    def app_index(self, request, app_label, extra_context=None):
        user = request.user
        has_module_perms = user.has_module_perms(app_label)
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                config = {}
                if app_label in self.index_config.keys():
                    config = self.index_config[app_label]

                if 'models' in config:
                    if model._meta.object_name not in config['models']:
                        continue
                
                app_title = config.get('label', app_label)
                app_caption = config.get('caption', '')
                hide_links = config.get('hide_links', False)

                if has_module_perms:
                    perms = {
                        'add': user.has_perm("%s.%s" % (app_label, model._meta.get_add_permission())),
                        'change': user.has_perm("%s.%s" % (app_label, model._meta.get_change_permission())),
                        'delete': user.has_perm("%s.%s" % (app_label, model._meta.get_delete_permission())),
                    }
                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        model_dict = {
                            'name': capfirst(model._meta.verbose_name_plural),
                            'admin_url': '%s/' % model.__name__.lower(),
                            'perms': perms,
                            'order': 0
                        }
                        if 'models' in config:
                            model_dict['order'] = config['models'].index(model._meta.object_name)

                        if app_dict:
                            app_dict['models'].append(model_dict),
                        else:
                            # First time around, now that we know there's
                            # something to display, add in the necessary meta
                            # information.
                            app_dict = {
                                'name': app_title.title(),
                                'caption': app_caption,
                                'app_url': '',
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                                'hide_links': hide_links
                            }
        if not app_dict:
            raise http.Http404('The requested admin page does not exist.')
        
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(lambda x, y: cmp(x['name'], y['name']))
        app_dict['models'].sort(lambda x, y: cmp(x['order'], y['order']))

        context = {
            'title': _('%s administration') % capfirst(app_label),
            'app_list': [app_dict],
            'root_path': self.root_path,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response(self.app_index_template or ('admin/%s/app_index.html' % app_label,
            'admin/app_index.html'), context,
            context_instance=context_instance
        )
