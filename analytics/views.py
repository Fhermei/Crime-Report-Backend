from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from reports.models import CrimeReport
from reports.permissions import IsPoliceOrAdmin

class DashboardStatsView(APIView):
    permission_classes = [IsPoliceOrAdmin]

    def get(self, request):
        qs = CrimeReport.objects.all()

        total = qs.count()
        pending = qs.filter(status="pending").count()
        investigating = qs.filter(status="investigating").count()
        resolved = qs.filter(status="resolved").count()
        emergency = qs.filter(urgency="emergency").count()

        by_type = list(qs.values("crime_type").annotate(count=Count("id")).order_by("-count"))
        by_urgency = list(qs.values("urgency").annotate(count=Count("id")).order_by("urgency"))
        by_status = [
            {"status": "pending", "count": pending},
            {"status": "investigating", "count": investigating},
            {"status": "resolved", "count": resolved},
        ]

        since = timezone.now() - timedelta(days=14)
        daily = (
            qs.filter(created_at__gte=since)
            .annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        daily_trend = [{"date": row["day"].strftime("%b %d"), "count": row["count"]} for row in daily]

        since_months = timezone.now() - timedelta(days=180)
        monthly = (
            qs.filter(created_at__gte=since_months)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        monthly_trend = [{"month": row["month"].strftime("%b %Y"), "count": row["count"]} for row in monthly]

        recent = list(
            qs.order_by("-created_at")[:8].values(
                "tracking_code", "crime_type", "urgency", "status", "created_at", "address"
            )
        )
        for r in recent:
            r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M")

        return Response({
            "generated_at": timezone.now().isoformat(),
            "totals": {
                "total": total,
                "pending": pending,
                "investigating": investigating,
                "resolved": resolved,
                "emergency": emergency,
            },
            "by_type": by_type,
            "by_urgency": by_urgency,
            "by_status": by_status,
            "daily_trend": daily_trend,
            "monthly_trend": monthly_trend,
            "recent_reports": recent,
        })