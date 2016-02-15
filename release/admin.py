from django.contrib import admin
from release.models import *


# Register your models here.

# class ProjectAdmin(admin.ModelAdmin):
#     list_display = (
#     'name', 'bproject', 'code_type', 'repo_type', 'repo_url', 'key_path', 'username', 'password', 'hostlist',
#     'server_path', 'desc')
#     search_fields = ('name', 'bproject', 'code_type', 'repo_type', 'hostlist', 'server_path')
#
#
# class AssetsAdmin(admin.ModelAdmin):
#     list_display = ('hostname', 'ip', 'service', 'sa', 'environment', 'desc')
#     search_fields = ('hostname', 'ip', 'service', 'sa', 'environment', 'desc')
#
#
# class SvnInfoAdmin(admin.ModelAdmin):
#     list_display = ('bproject', 'code_type', 'url', 'username', 'password', 'prehostlist', 'prohostlist', 'server_path')
#     search_fields = (
#     'bproject', 'code_type', 'url', 'username', 'password', 'prehostlist', 'prohostlist', 'server_path')
#
# admin.site.register(Project, ProjectAdmin)
# admin.site.register(Assets, AssetsAdmin)
# admin.site.register(SvnInfo, SvnInfoAdmin)
