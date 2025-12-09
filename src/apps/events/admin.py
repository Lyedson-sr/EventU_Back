from django.contrib import admin
from .models import Event, EventOccurrences

class EventOccurrencesInline(admin.TabularInline):
    model = EventOccurrences
    extra = 0 
    readonly_fields = ('created_at', 'updated_at')
    can_delete = True
    
    # Limita o queryset para melhor performance
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event')

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'event_type', 'group', 'start_datetime', 'end_datetime', 'occurrence_count')
    list_filter = ('event_type', 'start_datetime', 'created_at', 'group')
    search_fields = ('title', 'description', 'location', 'creator__email', 'creator__name', 'group__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('creator', 'group')
    
    # Mostra as ocorrências inline no admin do Event
    inlines = [EventOccurrencesInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'creator', 'group', 'event_type', 'color')
        }),
        ('Detalhes do Evento', {
            'fields': ('description', 'location')
        }),
        ('Data e Hora', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Recorrência', {
            'fields': ('recurrence_rrule', 'recurrence_exceptions'),
            'classes': ('collapse',) 
        }),
        ('Datas do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def occurrence_count(self, obj):
        return obj.occurrences.count()
    occurrence_count.short_description = 'Ocorrências'

class EventOccurrencesAdmin(admin.ModelAdmin):
    list_display = ('get_event_title', 'get_event_creator', 'occurrence_start', 'occurrence_end', 'cancelled')
    list_filter = ('cancelled', 'occurrence_start', 'occurrence_end')
    search_fields = ('event__title', 'event__creator__email', 'event__creator__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('event',)
    
    # Campos customizados para mostrar informações do evento
    def get_event_title(self, obj):
        return obj.event.title
    get_event_title.short_description = 'Evento'
    get_event_title.admin_order_field = 'event__title'
    
    def get_event_creator(self, obj):
        return obj.event.creator.email
    get_event_creator.short_description = 'Criador'
    get_event_creator.admin_order_field = 'event__creator__email'
    
    fieldsets = (
        (None, {
            'fields': ('event', 'cancelled')
        }),
        ('Data e Hora da Ocorrência', {
            'fields': ('occurrence_start', 'occurrence_end')
        }),
        ('Datas do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Para melhor performance com muitos registros
    list_select_related = ('event', 'event__creator')
    list_per_page = 50

admin.site.register(Event, EventAdmin)
admin.site.register(EventOccurrences, EventOccurrencesAdmin)