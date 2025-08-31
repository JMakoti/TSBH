from django.core.management.base import BaseCommand
from scholarships.models import County


class Command(BaseCommand):
    help = 'Populate the database with Kenyan counties data'

    def handle(self, *args, **options):
        counties_data = [
            {'name': 'baringo', 'code': '030', 'capital_city': 'Kabarnet'},
            {'name': 'bomet', 'code': '036', 'capital_city': 'Bomet'},
            {'name': 'bungoma', 'code': '039', 'capital_city': 'Bungoma'},
            {'name': 'busia', 'code': '040', 'capital_city': 'Busia'},
            {'name': 'elgeyo_marakwet', 'code': '028', 'capital_city': 'Iten'},
            {'name': 'embu', 'code': '014', 'capital_city': 'Embu'},
            {'name': 'garissa', 'code': '007', 'capital_city': 'Garissa'},
            {'name': 'homa_bay', 'code': '043', 'capital_city': 'Homa Bay'},
            {'name': 'isiolo', 'code': '011', 'capital_city': 'Isiolo'},
            {'name': 'kajiado', 'code': '034', 'capital_city': 'Kajiado'},
            {'name': 'kakamega', 'code': '037', 'capital_city': 'Kakamega'},
            {'name': 'kericho', 'code': '035', 'capital_city': 'Kericho'},
            {'name': 'kiambu', 'code': '022', 'capital_city': 'Kiambu'},
            {'name': 'kilifi', 'code': '003', 'capital_city': 'Kilifi'},
            {'name': 'kirinyaga', 'code': '020', 'capital_city': 'Kerugoya'},
            {'name': 'kisii', 'code': '045', 'capital_city': 'Kisii'},
            {'name': 'kisumu', 'code': '042', 'capital_city': 'Kisumu'},
            {'name': 'kitui', 'code': '015', 'capital_city': 'Kitui'},
            {'name': 'kwale', 'code': '002', 'capital_city': 'Kwale'},
            {'name': 'laikipia', 'code': '031', 'capital_city': 'Nanyuki'},
            {'name': 'lamu', 'code': '005', 'capital_city': 'Lamu'},
            {'name': 'machakos', 'code': '016', 'capital_city': 'Machakos'},
            {'name': 'makueni', 'code': '017', 'capital_city': 'Wote'},
            {'name': 'mandera', 'code': '009', 'capital_city': 'Mandera'},
            {'name': 'marsabit', 'code': '010', 'capital_city': 'Marsabit'},
            {'name': 'meru', 'code': '012', 'capital_city': 'Meru'},
            {'name': 'migori', 'code': '044', 'capital_city': 'Migori'},
            {'name': 'mombasa', 'code': '001', 'capital_city': 'Mombasa'},
            {'name': 'murang\'a', 'code': '021', 'capital_city': 'Murang\'a'},
            {'name': 'nairobi', 'code': '047', 'capital_city': 'Nairobi'},
            {'name': 'nakuru', 'code': '032', 'capital_city': 'Nakuru'},
            {'name': 'nandi', 'code': '029', 'capital_city': 'Kapsabet'},
            {'name': 'narok', 'code': '033', 'capital_city': 'Narok'},
            {'name': 'nyamira', 'code': '046', 'capital_city': 'Nyamira'},
            {'name': 'nyandarua', 'code': '018', 'capital_city': 'Ol Kalou'},
            {'name': 'nyeri', 'code': '019', 'capital_city': 'Nyeri'},
            {'name': 'samburu', 'code': '025', 'capital_city': 'Maralal'},
            {'name': 'siaya', 'code': '041', 'capital_city': 'Siaya'},
            {'name': 'taita_taveta', 'code': '006', 'capital_city': 'Voi'},
            {'name': 'tana_river', 'code': '004', 'capital_city': 'Hola'},
            {'name': 'tharaka_nithi', 'code': '013', 'capital_city': 'Chuka'},
            {'name': 'trans_nzoia', 'code': '026', 'capital_city': 'Kitale'},
            {'name': 'turkana', 'code': '023', 'capital_city': 'Lodwar'},
            {'name': 'uasin_gishu', 'code': '027', 'capital_city': 'Eldoret'},
            {'name': 'vihiga', 'code': '038', 'capital_city': 'Vihiga'},
            {'name': 'wajir', 'code': '008', 'capital_city': 'Wajir'},
            {'name': 'west_pokot', 'code': '024', 'capital_city': 'Kapenguria'},
        ]

        created_count = 0
        updated_count = 0

        for county_data in counties_data:
            county, created = County.objects.get_or_create(
                name=county_data['name'],
                defaults={
                    'code': county_data['code'],
                    'capital_city': county_data['capital_city']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created county: {county.get_name_display()}')
                )
            else:
                # Update existing county if needed
                if county.code != county_data['code'] or county.capital_city != county_data['capital_city']:
                    county.code = county_data['code']
                    county.capital_city = county_data['capital_city']
                    county.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated county: {county.get_name_display()}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed counties: {created_count} created, {updated_count} updated'
            )
        )
