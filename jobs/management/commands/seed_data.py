"""
Management command to seed Lancr with fake Irish profiles, jobs, applications and reviews.

Usage:
    python manage.py seed_data           # creates all fake data
    python manage.py seed_data --clear   # wipes existing seeded data first
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from jobs.models import Job, Application, Profile, Review, Notification
from decimal import Decimal
import random

User = get_user_model()

# ---------------------------------------------------------------------------
# Fake data pools
# ---------------------------------------------------------------------------

FREELANCERS = [
    {
        'username': 'sean_murphy_elec',
        'first_name': 'Seán',
        'last_name': 'Murphy',
        'email': 'sean.murphy@example.ie',
        'trade': 'Electrician',
        'county': 'Dublin',
        'hourly_rate': 65,
        'years_experience': 12,
        'bio': 'Qualified electrician with 12 years experience. Covering Dublin, Meath and Kildare. No job too small — from rewiring to fuse board upgrades. Fully insured and registered with RECI.',
        'is_available': True,
    },
    {
        'username': 'padraic_kelly_plumb',
        'first_name': 'Pádraic',
        'last_name': 'Kelly',
        'email': 'padraic.kelly@example.ie',
        'trade': 'Plumber',
        'county': 'Meath',
        'hourly_rate': 70,
        'years_experience': 15,
        'bio': 'Fully insured plumber based in Navan. Specialising in boiler installs, bathroom fitting and emergency callouts across Leinster. Gas Safe registered.',
        'is_available': True,
    },
    {
        'username': 'aoife_brennan_paint',
        'first_name': 'Aoife',
        'last_name': 'Brennan',
        'email': 'aoife.brennan@example.ie',
        'trade': 'Painter & Decorator',
        'county': 'Louth',
        'hourly_rate': 45,
        'years_experience': 8,
        'bio': 'Interior and exterior painting. Attention to detail guaranteed. Available weekdays and weekends across Louth and Meath. Free quotes given.',
        'is_available': True,
    },
    {
        'username': 'ciaran_walsh_carp',
        'first_name': 'Ciarán',
        'last_name': 'Walsh',
        'email': 'ciaran.walsh@example.ie',
        'trade': 'Carpenter',
        'county': 'Kildare',
        'hourly_rate': 60,
        'years_experience': 15,
        'bio': 'Bespoke furniture, fitted wardrobes, decking and general joinery. 15 years in the trade. Free quotes given. Based in Maynooth, covering all of Kildare and West Dublin.',
        'is_available': True,
    },
    {
        'username': 'niamh_obrien_garden',
        'first_name': 'Niamh',
        'last_name': "O'Brien",
        'email': 'niamh.obrien@example.ie',
        'trade': 'Landscaper',
        'county': 'Dublin',
        'hourly_rate': 40,
        'years_experience': 6,
        'bio': 'Garden design, lawn care, hedge trimming and seasonal tidy-ups. Serving West Dublin and Kildare. Fully insured with own equipment and van.',
        'is_available': True,
    },
    {
        'username': 'tomas_dunne_handyman',
        'first_name': 'Tomás',
        'last_name': 'Dunne',
        'email': 'tomas.dunne@example.ie',
        'trade': 'Handyman',
        'county': 'Offaly',
        'hourly_rate': 40,
        'years_experience': 10,
        'bio': 'No job too small. Flatpack assembly, tiling, odd jobs around the house. Reliable and punctual. Based in Tullamore, covering Offaly and surrounding counties.',
        'is_available': True,
    },
    {
        'username': 'declan_farrell_roof',
        'first_name': 'Declan',
        'last_name': 'Farrell',
        'email': 'declan.farrell@example.ie',
        'trade': 'Roofer',
        'county': 'Wicklow',
        'hourly_rate': 75,
        'years_experience': 18,
        'bio': 'Slate, tile and flat roof specialist. Guttering and fascia replacement. Covering Wicklow and South Dublin. All work guaranteed.',
        'is_available': False,
    },
    {
        'username': 'sinead_byrne_clean',
        'first_name': 'Sinéad',
        'last_name': 'Byrne',
        'email': 'sinead.byrne@example.ie',
        'trade': 'Cleaner',
        'county': 'Laois',
        'hourly_rate': 25,
        'years_experience': 5,
        'bio': 'Domestic and commercial cleaning. End-of-tenancy specialists. Fully insured with own equipment. Based in Portlaoise, covering Laois and surrounding areas.',
        'is_available': True,
    },
    {
        'username': 'brian_connolly_tile',
        'first_name': 'Brian',
        'last_name': 'Connolly',
        'email': 'brian.connolly@example.ie',
        'trade': 'Tiler',
        'county': 'Meath',
        'hourly_rate': 55,
        'years_experience': 9,
        'bio': 'Floor and wall tiling specialist. Bathrooms, kitchens and hallways. Based in Trim, covering all of Meath and North Dublin.',
        'is_available': True,
    },
    {
        'username': 'mairead_hayes_clean',
        'first_name': 'Máiréad',
        'last_name': 'Hayes',
        'email': 'mairead.hayes@example.ie',
        'trade': 'Cleaner',
        'county': 'Kildare',
        'hourly_rate': 28,
        'years_experience': 7,
        'bio': 'Professional domestic cleaner based in Newbridge. Weekly, fortnightly or one-off cleans. Fully vetted and insured.',
        'is_available': True,
    },
]

CLIENTS = [
    {'username': 'john_doyle_client', 'first_name': 'John', 'last_name': 'Doyle', 'email': 'john.doyle@example.ie'},
    {'username': 'mary_flanagan_client', 'first_name': 'Mary', 'last_name': 'Flanagan', 'email': 'mary.flanagan@example.ie'},
    {'username': 'patrick_ryan_client', 'first_name': 'Patrick', 'last_name': 'Ryan', 'email': 'patrick.ryan@example.ie'},
    {'username': 'siobhan_mcgrath_client', 'first_name': 'Siobhán', 'last_name': 'McGrath', 'email': 'siobhan.mcgrath@example.ie'},
    {'username': 'eoin_burke_client', 'first_name': 'Eoin', 'last_name': 'Burke', 'email': 'eoin.burke@example.ie'},
]

JOBS = [
    {
        'title': 'Bathroom rewire needed in Navan',
        'description': 'Looking for a qualified electrician to rewire our main bathroom. House is from the 1980s so wiring needs full update. Must be RECI registered.',
        'budget': 800,
        'category': 'electrical',
        'location': 'Navan, Co. Meath',
        'status': 'open',
    },
    {
        'title': 'Boiler replacement — Lucan, Dublin',
        'description': 'Our old oil boiler has given up. Looking for a plumber to install a new gas combi boiler. Supply and fit. Get in touch with quotes.',
        'budget': 2200,
        'category': 'plumbing',
        'location': 'Lucan, Co. Dublin',
        'status': 'open',
    },
    {
        'title': 'Full interior repaint — 3 bed semi in Drogheda',
        'description': 'Need full interior painted — all rooms, ceilings, doors and skirting. House is empty so flexible on timing. Looking for a tidy job.',
        'budget': 1800,
        'category': 'painting',
        'location': 'Drogheda, Co. Louth',
        'status': 'open',
    },
    {
        'title': 'Garden clearance and tidy — Maynooth',
        'description': 'Back garden has gotten completely out of hand. Hedges need cutting back, lawn needs mowing and some old timber needs removed. Half day job roughly.',
        'budget': 350,
        'category': 'landscaping',
        'location': 'Maynooth, Co. Kildare',
        'status': 'open',
    },
    {
        'title': 'Fitted wardrobe — master bedroom, Wicklow town',
        'description': 'Looking for a carpenter to build a fitted wardrobe in the master bedroom. Alcove space is roughly 3m wide. Sliding doors preferred.',
        'budget': 1200,
        'category': 'carpentry',
        'location': 'Wicklow Town',
        'status': 'open',
    },
    {
        'title': 'Roof inspection and repair — Portlaoise',
        'description': 'Noticed some damp on the ceiling after the last few storms. Think a few slates may have shifted. Need someone to inspect and fix as needed.',
        'budget': 600,
        'category': 'construction',
        'location': 'Portlaoise, Co. Laois',
        'status': 'open',
    },
    {
        'title': 'End of tenancy clean — 2 bed apartment, Dublin 8',
        'description': 'Vacating a 2 bed apartment and need a full end of tenancy clean. Needs to be to a high standard for landlord inspection. ASAP preferred.',
        'budget': 220,
        'category': 'cleaning',
        'location': 'Dublin 8',
        'status': 'open',
    },
    {
        'title': 'Kitchen floor tiling — Trim, Co. Meath',
        'description': 'Kitchen floor needs retiling. Roughly 20sqm. Tiles already purchased. Just need supply of adhesive, grout and labour.',
        'budget': 700,
        'category': 'other',
        'location': 'Trim, Co. Meath',
        'status': 'open',
    },
]

REVIEW_COMMENTS = [
    "Really happy with the work. Would definitely use again.",
    "Showed up on time, did a great job and left the place clean. Highly recommend.",
    "Excellent tradesperson. Fair price and quality finish.",
    "Very professional. Kept us informed throughout and completed ahead of schedule.",
    "Good work overall. Took a little longer than expected but result was great.",
    "Brilliant job. Very tidy worker and great attention to detail.",
    "Would highly recommend to anyone in the area. Top quality work.",
]


class Command(BaseCommand):
    help = 'Seed the database with fake Irish freelancer and client data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete previously seeded users before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing seeded data...')
            seeded_usernames = (
                [f['username'] for f in FREELANCERS] +
                [c['username'] for c in CLIENTS]
            )
            User.objects.filter(username__in=seeded_usernames).delete()
            self.stdout.write(self.style.SUCCESS('Cleared.'))

        self.stdout.write('Creating freelancers...')
        freelancer_users = []
        for data in FREELANCERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()

            profile = user.profile
            profile.role = 'freelancer'
            profile.bio = data['bio']
            profile.trade = data['trade']
            profile.county = data['county']
            profile.hourly_rate = Decimal(str(data['hourly_rate']))
            profile.years_experience = data['years_experience']
            profile.is_available = data['is_available']
            profile.save()

            freelancer_users.append(user)
            self.stdout.write(f'  ✓ {user.get_full_name()} ({data["trade"]}, {data["county"]})')

        self.stdout.write('Creating clients...')
        client_users = []
        for data in CLIENTS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()

            profile = user.profile
            profile.role = 'client'
            profile.save()

            client_users.append(user)
            self.stdout.write(f'  ✓ {user.get_full_name()}')

        self.stdout.write('Creating jobs...')
        created_jobs = []
        for i, job_data in enumerate(JOBS):
            client = client_users[i % len(client_users)]
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                defaults={
                    'description': job_data['description'],
                    'budget': Decimal(str(job_data['budget'])),
                    'category': job_data['category'],
                    'location': job_data['location'],
                    'status': job_data['status'],
                    'client': client,
                    'currency': 'EUR',
                }
            )
            created_jobs.append(job)
            self.stdout.write(f'  ✓ {job.title}')

        self.stdout.write('Creating applications...')
        for job in created_jobs[:4]:
            applicants = random.sample(freelancer_users, min(3, len(freelancer_users)))
            for freelancer in applicants:
                Application.objects.get_or_create(
                    job=job,
                    freelancer=freelancer,
                    defaults={'cover_letter': f'Hi, I am very interested in this job. I have relevant experience and am available to start soon. Please feel free to get in touch.', 'status': 'pending'}
                )

        self.stdout.write('Creating reviews...')
        for i, freelancer in enumerate(freelancer_users[:6]):
            client = client_users[i % len(client_users)]
            job = created_jobs[i % len(created_jobs)]
            if not Review.objects.filter(job=job, reviewer=client).exists():
                Review.objects.create(
                    job=job,
                    reviewer=client,
                    reviewee=freelancer,
                    rating=random.choice([4, 4, 5, 5, 5]),
                )
                self.stdout.write(f'  ✓ Review for {freelancer.get_full_name()}')

        self.stdout.write(self.style.SUCCESS('\n✅ Seed complete!'))
        self.stdout.write(f'   {len(freelancer_users)} freelancers')
        self.stdout.write(f'   {len(client_users)} clients')
        self.stdout.write(f'   {len(created_jobs)} jobs')
        self.stdout.write('   All passwords: testpass123')