from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import shutil, os

class Command(BaseCommand):
    help = 'Initiates the database'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        #copy clueless.py to the account_keeping folder
        current_folder = dirpath = os.getcwd()
        #current_folder= 'C:\\Users\\Einstein Millan\\condoaldia\\condominioaldia'
        from_folder = os.path.join(current_folder, 'condo_manager', 'clueless.py')
        to_folder = os.path.join(current_folder, 'account_keeping', 'migrations' )
        # adding exception handling
        try:
            shutil.copy(from_folder, to_folder)
            call_command("makemigrations") #, interactive=False
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", sys.exc_info())
        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)

        #     poll.opened = False
        #     poll.save()

        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))