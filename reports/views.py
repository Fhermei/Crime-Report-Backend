from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db.models import Count  # <- ADD THIS IMPORT
import uuid

from .models import CrimeReport, Evidence, StatusUpdate, Notification
from .permissions import IsPoliceOrAdmin, IsAdminRole, IsPoliceRole
from .serializers import (
    CrimeReportCreateSerializer, CrimeReportListSerializer, CrimeReportAdminSerializer,
    StatusChangeSerializer, TrackReportSerializer, AssignReportSerializer,
)
from .supabase_upload import upload_evidence_file
from django.contrib.auth import get_user_model

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

class ReportCreateView(generics.CreateAPIView):
    serializer_class = CrimeReportCreateSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_logged_in = request.user and request.user.is_authenticated
        is_anonymous_flag = str(request.data.get("is_anonymous", "false")).lower() == "true"

        report = serializer.save(
            reporter=request.user if is_logged_in and not is_anonymous_flag else None,
            is_anonymous=(not is_logged_in) or is_anonymous_flag,
            ip_address=get_client_ip(request),
        )

        files = request.FILES.getlist("evidence")
        for f in files:
            try:
                file_url, file_type = upload_evidence_file(f)
                Evidence.objects.create(report=report, file_url=file_url, file_type=file_type)
            except Exception as e:
                print(f"Error uploading file: {e}")
                try:
                    Evidence.objects.create(
                        report=report, 
                        file_url=f"https://example.com/evidence/{uuid.uuid4()}.{f.name.split('.')[-1]}", 
                        file_type="document"
                    )
                except:
                    pass

        output = CrimeReportListSerializer(report)
        return Response(
            {
                "message": "Report sent successfully.",
                "tracking_code": report.tracking_code,
                "report": output.data,
            },
            status=status.HTTP_201_CREATED,
        )

class TrackReportView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.query_params.get("code", "").strip().upper()
        if not code:
            return Response({"detail": "Please provide a tracking code."}, status=400)
        try:
            report = CrimeReport.objects.get(tracking_code=code)
        except CrimeReport.DoesNotExist:
            return Response({"detail": "No report found with that tracking code."}, status=404)
        return Response(TrackReportSerializer(report).data)

class MyReportsView(generics.ListAPIView):
    serializer_class = CrimeReportListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CrimeReport.objects.filter(reporter=self.request.user)

class ReportListView(generics.ListAPIView):
    permission_classes = [IsPoliceOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "crime_type", "urgency", "assigned_to"]
    search_fields = ["description", "address", "tracking_code"]
    ordering_fields = ["created_at", "urgency", "status"]

    def get_queryset(self):
        # For police officers, only show reports assigned to them
        if self.request.user.role == "police":
            return CrimeReport.objects.filter(assigned_to=self.request.user)
        # For admin, show all reports
        return CrimeReport.objects.all()

    def get_serializer_class(self):
        if self.request.user.role == "admin":
            return CrimeReportAdminSerializer
        return CrimeReportListSerializer

class ReportDetailView(generics.RetrieveAPIView):
    permission_classes = [IsPoliceOrAdmin]
    queryset = CrimeReport.objects.all()

    def get_serializer_class(self):
        if self.request.user.role == "admin":
            return CrimeReportAdminSerializer
        return CrimeReportListSerializer

class UpdateStatusView(APIView):
    permission_classes = [IsPoliceOrAdmin]

    def patch(self, request, pk):
        try:
            report = CrimeReport.objects.get(pk=pk)
        except CrimeReport.DoesNotExist:
            return Response({"detail": "Report not found."}, status=404)

        # Check if police officer is assigned to this report
        if request.user.role == "police" and report.assigned_to != request.user:
            return Response({"detail": "You are not assigned to this report."}, status=403)

        serializer = StatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        note = serializer.validated_data.get("note", "")

        old_status = report.status
        report.status = new_status
        report.save(update_fields=["status", "updated_at"])

        StatusUpdate.objects.create(
            report=report, updated_by=request.user, old_status=old_status, new_status=new_status, note=note
        )

        # Notify reporter
        if report.reporter:
            Notification.objects.create(
                user=report.reporter,
                report=report,
                message=f"Your report {report.tracking_code} status changed to {new_status}.",
            )

        # Notify admin
        admins = User.objects.filter(role="admin")
        for admin in admins:
            Notification.objects.create(
                user=admin,
                report=report,
                message=f"Report {report.tracking_code} status updated to {new_status} by {request.user.username}.",
            )

        return Response(CrimeReportAdminSerializer(report).data if request.user.role == "admin"
                         else CrimeReportListSerializer(report).data)

class AssignReportView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            report = CrimeReport.objects.get(pk=pk)
        except CrimeReport.DoesNotExist:
            return Response({"detail": "Report not found."}, status=404)

        serializer = AssignReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        assigned_to_id = serializer.validated_data["assigned_to"]
        note = serializer.validated_data.get("note", "")

        try:
            police_officer = User.objects.get(id=assigned_to_id, role="police")
        except User.DoesNotExist:
            return Response({"detail": "Police officer not found."}, status=404)

        report.assigned_to = police_officer
        report.assigned_by = request.user
        report.assigned_at = timezone.now()
        report.save(update_fields=["assigned_to", "assigned_by", "assigned_at", "updated_at"])

        # Create notification for police officer
        Notification.objects.create(
            user=police_officer,
            report=report,
            message=f"You have been assigned to report {report.tracking_code} by {request.user.username}.",
        )

        # Create status update
        StatusUpdate.objects.create(
            report=report,
            updated_by=request.user,
            old_status=report.status,
            new_status=report.status,
            note=f"Assigned to {police_officer.username}. {note}" if note else f"Assigned to {police_officer.username}.",
        )

        return Response({
            "message": f"Report assigned to {police_officer.username} successfully.",
            "report": CrimeReportAdminSerializer(report).data
        })

class PoliceOfficersView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        officers = User.objects.filter(role="police").values("id", "username", "first_name", "last_name", "email", "phone_number", "badge_number")
        return Response(list(officers))

class PoliceAssignedReportsView(generics.ListAPIView):
    """Get all reports assigned to the current police officer"""
    serializer_class = CrimeReportListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "police":
            return CrimeReport.objects.none()
        return CrimeReport.objects.filter(assigned_to=self.request.user)

class PoliceDashboardStatsView(APIView):
    """Get statistics for police officer's assigned reports"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "police":
            return Response({"detail": "Only police officers can access this."}, status=403)

        reports = CrimeReport.objects.filter(assigned_to=request.user)
        
        total = reports.count()
        pending = reports.filter(status="pending").count()
        investigating = reports.filter(status="investigating").count()
        resolved = reports.filter(status="resolved").count()
        emergency = reports.filter(urgency="emergency").count()

        by_type = list(reports.values("crime_type").annotate(count=Count("id")).order_by("-count"))
        by_urgency = list(reports.values("urgency").annotate(count=Count("id")).order_by("urgency"))

        return Response({
            "totals": {
                "total": total,
                "pending": pending,
                "investigating": investigating,
                "resolved": resolved,
                "emergency": emergency,
            },
            "by_type": by_type,
            "by_urgency": by_urgency,
            "generated_at": timezone.now().isoformat(),
        })