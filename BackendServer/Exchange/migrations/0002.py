from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def load_companies(apps, schema_editor):
    Company = apps.get_model("Exchange","Company")
    names = ["Amper","Marcel","Lidl","Biedronka","Microsoft","Facebook",
    "Twitter","Google","Vivat","Signea","Mexa","PKO","Nork","Volvo","Vego",
    "Nefi","Finanseo","Axol","RopPol","LeoSport","Platigo","Tevo","Selos",
    "Exiro","Fortim","Vermon","Tevi","Dinos","Budex","Res Gastro","Garmnik",
    "Max Burger","Sony","Ebay","Nissan","Reebok","Lego","Umbrella","NFZ","PRZ",
    "Carrer","GoldAlpha","Electa","Funvita","Empik","House","Sephora","Rossmann",
    "Jackobs","ALG Pharma",]
    i=0
    for n in names:
        compx = Company(id=i, name=n)
        compx.save()
        i=i+1
    
def delete_companies(apps, schema_editor):
    Company = apps.get_model("Exchange","Company")
    Company.objects.all().delete()
    
class Migration(migrations.Migration):
    dependencies = [
        ('Exchange', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_companies,delete_companies),
    ]