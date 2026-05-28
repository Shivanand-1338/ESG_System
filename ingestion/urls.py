"""
URL configuration for the ingestion API.
"""

from django.urls import path
from . import views
from . import auth_views

app_name = 'ingestion'

urlpatterns = [
    # Authentication
    path('auth/login/', auth_views.login_view, name='auth_login'),
    path('auth/logout/', auth_views.logout_view, name='auth_logout'),
    path('auth/user/', auth_views.user_info, name='auth_user'),
    
    # Data Ingestion
    path('ingest/sap/', views.ingest_sap, name='ingest_sap'),
    path('ingest/greenbutton/', views.ingest_greenbutton, name='ingest_greenbutton'),
    path('ingest/concur/', views.ingest_concur, name='ingest_concur'),
    
    # Data Retrieval
    path('records/', views.record_list, name='record_list'),
    path('records/suspicious/', views.suspicious_records, name='suspicious_records'),
    path('records/bulk-approve/', views.bulk_approve, name='bulk_approve'),
    path('records/<uuid:record_id>/', views.record_detail, name='record_detail'),
    path('records/<uuid:record_id>/audit-trail/', views.record_audit_trail, name='record_audit_trail'),
    
    # Approval Workflow
    path('records/<uuid:record_id>/approve/', views.approve_record, name='approve_record'),
    path('records/<uuid:record_id>/unapprove/', views.unapprove_record, name='unapprove_record'),
    path('records/<uuid:record_id>/dismiss-flag/', views.dismiss_flag, name='dismiss_flag'),
    
    # Statistics
    path('statistics/summary/', views.statistics_summary, name='statistics_summary'),
    path('statistics/by-scope/', views.statistics_by_scope, name='statistics_by_scope'),
]
