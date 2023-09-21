
from dateutil.relativedelta import relativedelta
from edc_base import get_utcnow
from django.apps import apps as django_apps
from django.conf import settings
from django.forms import model_to_dict
from edc_model_wrapper import ModelWrapper
from .facet_screening_model_wrapper import FacetScreeningModelWrapper
from .facet_consent_model_wrapper import FacetConsentModelWrapper
from ..models import FacetSubjectScreening, FacetConsent
from ..utils import age_in_months


class FlourishConsentModelWrapper(ModelWrapper):
    model = 'flourish_caregiver.subjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'facet_flourish_consent_listboard_url')
    next_url_attrs = ['subject_identifier',]
    facet_screening_model = 'flourish_facet.facetsubjectscreening'
    facet_consent_model = 'flourish_facet.facetconsent'
    flourish_consent_model = 'flourish_caregiver.subjectconsent'

    @property
    def flourish_consent_cls(self):
        return django_apps.get_model(self.flourish_consent_model)

    @property
    def facet_screening_cls(self):
        return django_apps.get_model(self.facet_screening_model)

    @property
    def facet_consent_cls(self):
        return django_apps.get_model(self.facet_consent_model)

    @property
    def flourish_consent_obj(self):
        try:
            obj = self.flourish_consent_cls.objects.filter(
                subject_identifier=self.object.subject_identifier
            ).latest('consent_datetime')

        except self.flourish_consent_cls.DoesNotExist:
            pass
        else:
            return obj

    @property
    def facet_screening_obj(self):
        try:
            obj = self.facet_screening_cls.objects.filter(
                subject_identifier=self.object.subject_identifier
            ).latest('report_datetime')
        except self.facet_screening_cls.DoesNotExist:
            pass
        else:
            return obj

    @property
    def facet_consent_obj(self):
        try:
            obj = self.facet_consent_cls.objects.filter(
                subject_identifier=self.object.subject_identifier
            ).latest('report_datetime')
        except self.facet_consent_cls.DoesNotExist:
            pass
        else:
            return obj

    @property
    def facet_screening_wrapper(self):

        facet_screening_obj = self.facet_screening_obj or FacetSubjectScreening(
            subject_identifier=self.object.subject_identifier
        )

        return FacetScreeningModelWrapper(model_obj=facet_screening_obj)

    @property
    def facet_child_age(self):

        dates_before = (get_utcnow() - relativedelta(months=6)
                        ).date().isoformat()

        today = get_utcnow().date().isoformat()

        child_consents = self.object.caregiverchildconsent_set.filter(
            child_dob__range=[dates_before, today])

        ages = []
        for consent in child_consents:
            dob = consent.child_dob
            ages.append(str(age_in_months(dob)))

        return ', '.join(ages)

    @property
    def facet_consent_wrapper(self):

        target_fields = ['subject_identifier',
                         'consent_datetime',
                         'first_name',
                         'last_name',
                         'initials',
                         'language',
                         'is_literate',
                         'witness_name',
                         'gender',
                         'gender_other',
                         'dob',
                         'is_dob_estimated',
                         'identity',
                         'identity_type',
                         'confirm_identity',
                         'consent_to_participate',
                         'child_consent',]

        flourish_consent_dict = model_to_dict(instance=self.flourish_consent_obj,
                                              fields=target_fields)

        facet_consent_obj = self.facet_consent_obj or FacetConsent(
            **flourish_consent_dict
        )

        return FacetConsentModelWrapper(model_obj=facet_consent_obj)
