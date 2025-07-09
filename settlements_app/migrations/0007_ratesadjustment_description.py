from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("settlements_app", "0006_ratesadjustment"),
    ]

    operations = [
        migrations.AddField(
            model_name="ratesadjustment",
            name="description",
            field=models.CharField(
                choices=[
                    ("council_rates", "Council Rates"),
                    ("water", "Water"),
                    ("body_corp", "Body Corporate"),
                    ("other", "Other"),
                ],
                default="council_rates",
                max_length=50,
            ),
        ),
    ]
