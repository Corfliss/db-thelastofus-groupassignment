# Generated by Django 5.1.3 on 2024-12-09 19:37

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL(
            """
            -- SQL Script for sequence, function, and trigger
            CREATE SEQUENCE mypay_id_seq START WITH 1 INCREMENT BY 1;

            CREATE OR REPLACE FUNCTION generate_mypay_id()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.MyPayId := 'MP' || LPAD(nextval('mypay_id_seq')::TEXT, 3, '0');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER set_mypay_id
            BEFORE INSERT ON tr_mypay
            FOR EACH ROW
            EXECUTE FUNCTION generate_mypay_id();
            """
        ),
    ]
