from django.contrib import admin

# Analytics app doesn't have its own models, so admin is minimal
admin.site.site_header = "Crime Reporting System Admin"
admin.site.site_title = "Crime Reporting System"
admin.site.index_title = "Dashboard"