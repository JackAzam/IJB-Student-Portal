from django.db import transaction
from django.utils import timezone
from .models import Offer, AuditLog, StudentProfile

@transaction.atomic
def select_offer(*, offer_id, actor, reason=''):
    """Select one passed interview offer without deleting any interview/offer history."""
    offer = Offer.objects.select_related('interview__student').get(pk=offer_id)
    # Lock the student row so concurrent offer selections for the same student serialize.
    StudentProfile.objects.select_for_update().get(pk=offer.interview.student_id)
    offer = Offer.objects.select_for_update().select_related('interview__student').get(pk=offer_id)
    if offer.interview.status != offer.interview.Status.PASSED:
        raise ValueError('Hanya offer dari interview berstatus Passed yang dapat dipilih.')
    student_id = offer.interview.student_id
    previous = list(Offer.objects.filter(interview__student_id=student_id, status=Offer.Status.SELECTED).values_list('id', flat=True))
    Offer.objects.filter(interview__student_id=student_id).exclude(pk=offer.pk).filter(status=Offer.Status.SELECTED).update(status=Offer.Status.NOT_SELECTED)
    offer.status = Offer.Status.SELECTED
    offer.selected_at = timezone.now()
    offer.selection_note = reason
    offer.save(update_fields=['status','selected_at','selection_note'])
    AuditLog.objects.create(actor=actor, action='OFFER_SELECTED', object_type='Offer', object_id=str(offer.pk), details={'previously_selected_offer_ids': previous, 'reason': reason})
    return offer
