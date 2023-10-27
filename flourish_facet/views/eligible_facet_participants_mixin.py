from django.apps import apps as django_apps
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
from edc_constants.constants import YES
from django.db.models import Max


class EligibleFacetParticipantsMixin:

    antenatal_enrollment_model = 'flourish_caregiver.antenatalenrollment'
    flourish_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    def antenatal_enrollment_cls(self):
        return django_apps.get_model(self.antenatal_enrollment_model)

    def flourish_child_consent_cls(self):
        return django_apps.get_model(self.flourish_child_consent_model)

    def eligible_participants(self, queryset):

        dates_before = (get_utcnow() - relativedelta(months=6, days=10)
                        ).date().isoformat()

        today = get_utcnow().date().isoformat()

        anc_subject_identifiers = self.antenatal_enrollment_cls.objects.values_list('subject_identifier',
                                                                                    flat=True)

        subject_identifiers = self.flourish_child_consent_cls.objects.filter(
            child_dob__range=[dates_before, today],
            subject_consent__subject_identifier__in=anc_subject_identifiers
        ).values_list('subject_consent__subject_identifier', flat=True)

        consent_ids = []

        for subject_identifier in subject_identifiers:

            consent = self.model_cls.objects.filter(
                subject_identifier = subject_identifier
            ).latest('version')

            consent_ids.append(consent.id)

        return queryset.filter(id__in=consent_ids,
                               subject_identifier__startswith='B',
                               future_contact=YES).annotate(
                                   child_dob=Max('caregiverchildconsent__child_dob'),).order_by('child_dob')