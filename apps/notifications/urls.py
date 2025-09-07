"""
URLs pour l'application notifications
"""

from django.urls import path
from .views import (
    # Notifications générales
    notification_list,
    notification_detail,
    notification_create,
    notification_stats,
    notification_retry,
    notification_cancel,
    notification_logs,
    notification_templates,
    notification_template_detail,
    
    # Notifications email
    email_notification_list,
    email_notification_detail,
    email_send,
    email_bulk_send,
    email_template_list,
    email_template_detail,
    email_template_create,
    email_template_update,
    email_template_delete,
    
    # Notifications SMS
    sms_notification_list,
    sms_notification_detail,
    sms_send,
    sms_bulk_send,
    sms_stats,
    
    # Notifications push
    push_notification_list,
    push_notification_detail,
    push_send,
    push_bulk_send,
    push_token_list,
    push_token_create,
    push_token_delete,
    push_token_update,
    push_stats,
)

app_name = 'notifications'

urlpatterns = [
    # Notifications générales
    path('', notification_list, name='notification_list'),
    path('create/', notification_create, name='notification_create'),
    path('stats/', notification_stats, name='notification_stats'),
    path('templates/', notification_templates, name='notification_templates'),
    path('templates/<int:template_id>/', notification_template_detail, name='notification_template_detail'),
    path('<int:notification_id>/', notification_detail, name='notification_detail'),
    path('<int:notification_id>/retry/', notification_retry, name='notification_retry'),
    path('<int:notification_id>/cancel/', notification_cancel, name='notification_cancel'),
    path('<int:notification_id>/logs/', notification_logs, name='notification_logs'),
    
    # Notifications email
    path('emails/', email_notification_list, name='email_notification_list'),
    path('emails/send/', email_send, name='email_send'),
    path('emails/bulk-send/', email_bulk_send, name='email_bulk_send'),
    path('emails/templates/', email_template_list, name='email_template_list'),
    path('emails/templates/create/', email_template_create, name='email_template_create'),
    path('emails/templates/<int:template_id>/', email_template_detail, name='email_template_detail'),
    path('emails/templates/<int:template_id>/update/', email_template_update, name='email_template_update'),
    path('emails/templates/<int:template_id>/delete/', email_template_delete, name='email_template_delete'),
    path('emails/<int:email_id>/', email_notification_detail, name='email_notification_detail'),
    
    # Notifications SMS
    path('sms/', sms_notification_list, name='sms_notification_list'),
    path('sms/send/', sms_send, name='sms_send'),
    path('sms/bulk-send/', sms_bulk_send, name='sms_bulk_send'),
    path('sms/stats/', sms_stats, name='sms_stats'),
    path('sms/<int:sms_id>/', sms_notification_detail, name='sms_notification_detail'),
    
    # Notifications push
    path('push/', push_notification_list, name='push_notification_list'),
    path('push/send/', push_send, name='push_send'),
    path('push/bulk-send/', push_bulk_send, name='push_bulk_send'),
    path('push/stats/', push_stats, name='push_stats'),
    path('push/tokens/', push_token_list, name='push_token_list'),
    path('push/tokens/create/', push_token_create, name='push_token_create'),
    path('push/tokens/<int:token_id>/update/', push_token_update, name='push_token_update'),
    path('push/tokens/<int:token_id>/delete/', push_token_delete, name='push_token_delete'),
    path('push/<int:push_id>/', push_notification_detail, name='push_notification_detail'),
]
