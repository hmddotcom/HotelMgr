from django.core.management.base import BaseCommand
from django.utils import timezone
from reservations.models import Reservation
from billing.models import Invoice, InvoiceLine
import datetime

class Command(BaseCommand):
    help = 'Charges the daily rate for all active reservations that have not been charged for the current day.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # On ne prend que les réservations actives dont la date de fin n'est pas encore passée
        active_reservations = Reservation.objects.filter(statut='active', date_fin__gte=today)
        
        self.stdout.write(f"Vérification des facturations journalières pour {active_reservations.count()} réservation(s) active(s) en date du {today.strftime('%d/%m/%Y')}.")
        
        charged_count = 0
        for reservation in active_reservations:
            try:
                # Trouver la facture impayée ou partiellement payée correspondante
                invoice = Invoice.objects.get(reservation=reservation, statut__in=['impaye', 'partiel'])
                
                # Description de la ligne de facture pour aujourd'hui
                description_today = f"Nuitée du {today.strftime('%d/%m/%Y')}"
                
                # Vérifier si une facturation pour aujourd'hui a déjà été faite pour éviter les doublons
                already_charged = invoice.lines.filter(description__startswith=description_today).exists()
                
                if not already_charged:
                    # Ajouter la ligne de facture pour la nuitée du jour
                    InvoiceLine.objects.create(
                        facture=invoice,
                        description=f"{description_today} - Chambre {reservation.chambre.numero}",
                        quantite=1,
                        prix_unitaire=reservation.chambre.room_group.price
                    )
                    
                    # Recalculer les totaux de la facture
                    invoice.calculer_totaux()
                    invoice.save()
                    
                    charged_count += 1
                    self.stdout.write(self.style.SUCCESS(f"-> Facturé avec succès pour la réservation #{reservation.id} (Client: {reservation.client.nom})."))
                else:
                    self.stdout.write(self.style.WARNING(f"-> La réservation #{reservation.id} a déjà été facturée pour aujourd'hui. Ignoré."))
            
            except Invoice.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"-> Aucune facture impayée trouvée pour la réservation active #{reservation.id}. Ignoré."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"-> Une erreur est survenue pour la réservation #{reservation.id}: {e}"))

        self.stdout.write(f"\nOpération terminée. {charged_count} réservation(s) ont été facturées pour la journée.")
