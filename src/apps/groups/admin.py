from django.contrib import admin
from .models import Group, GroupMember

class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1  # Número de forms vazios para adicionar novos members
    raw_id_fields = ('user',)  # Para performance com muitos usuários

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'color', 'created_at', 'member_count')
    list_filter = ('created_at', 'color')
    search_fields = ('name', 'description', 'creator__email', 'creator__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('creator',)  # Para performance com muitos usuários
    
    # Mostra os membros inline no admin do Group
    inlines = [GroupMemberInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'creator', 'color')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',) 
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        return obj.group_members.count()
    member_count.short_description = 'Membros'

class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('get_group_name', 'get_user_email', 'joined_at')
    list_filter = ('joined_at', 'group')
    search_fields = ('group__name', 'user__email', 'user__name')
    readonly_fields = ('joined_at',)
    raw_id_fields = ('group', 'user')
    
    # Campos customizados para mostrar nomes curtos
    def get_group_name(self, obj):
        return obj.group.name
    get_group_name.short_description = 'Grupo'
    get_group_name.admin_order_field = 'group__name'  # Permite ordenar
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Usuário'
    get_user_email.admin_order_field = 'user__email'  # Permite ordenar
    
    fieldsets = (
        (None, {
            'fields': ('group', 'user')
        }),
        ('Date', {
            'fields': ('joined_at',),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)