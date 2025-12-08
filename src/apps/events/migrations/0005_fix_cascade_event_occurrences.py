from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_eventguest"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE event_occurrences
            DROP CONSTRAINT IF EXISTS event_occurrences_event_id_209d76ff_fk_events_id;

            ALTER TABLE event_occurrences
            ADD CONSTRAINT event_occurrences_event_id_fk
            FOREIGN KEY (event_id)
            REFERENCES events(id)
            ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE event_occurrences
            DROP CONSTRAINT IF EXISTS event_occurrences_event_id_fk;
            """
        ),
    ]
