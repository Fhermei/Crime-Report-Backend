from django.urls import path
from .views import (
    ReportCreateView, TrackReportView, MyReportsView,
    ReportListView, ReportDetailView, UpdateStatusView,
    AssignReportView, PoliceOfficersView, PoliceAssignedReportsView,
    PoliceDashboardStatsView,
)

urlpatterns = [
    path("submit/", ReportCreateView.as_view(), name="report-submit"),
    path("track/", TrackReportView.as_view(), name="report-track"),
    path("mine/", MyReportsView.as_view(), name="report-mine"),
    path("", ReportListView.as_view(), name="report-list"),
    path("<uuid:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("<uuid:pk>/status/", UpdateStatusView.as_view(), name="report-status"),
    path("<uuid:pk>/assign/", AssignReportView.as_view(), name="report-assign"),
    path("police-officers/", PoliceOfficersView.as_view(), name="police-officers"),
    path("police/assigned/", PoliceAssignedReportsView.as_view(), name="police-assigned"),
    path("police/stats/", PoliceDashboardStatsView.as_view(), name="police-stats"),
]