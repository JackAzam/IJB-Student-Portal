
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from portal.models import (
    ExamRule,
    JobType,
    DocumentRequirement,
)


class Command(BaseCommand):
    help = (
        'Create initial IJB exam rules, job types, '
        'and configurable document checklist.'
    )

    def handle(self, *args, **options):
        # ========================================================
        # STAFF GROUP
        # ========================================================

        staff_group, _ = Group.objects.get_or_create(
            name='LPK Staff'
        )
        staff_group.permissions.clear()

        self.stdout.write(
            'LPK Staff group permissions: cleared (portal access only)'
        )

        # ========================================================
        # MANAGER GROUP
        # ========================================================

        manager_group, _ = Group.objects.get_or_create(
            name='LPK Managers'
        )

        manager_models = [
            # Existing models
            'studentprofile',
            'studentstaffassignment',
            'studentdocument',
            'jobtype',
            'tskkumiai',
            'tskcontact',
            'receivingcompany',
            'order',
            'studentorderassignment',
            'examrule',
            'examattempt',
            'medicalcheckup',
            'interview',
            'offer',
            'passportcase',
            'documentrequirement',
            'calendarevent',
            'supportticket',
            'ticketreply',
            'tskvisit',
            'placementcommunication',
            'auditlog',

            # New v1.03 models
            'studentworkflowitem',
            'workflowitemordersource',
            'documentversion',
            'documenttemplate',
            'documenttemplateversion',
            'kemenakerbatch',
            'kemenakerbatchevent',
            'kemenakerbatchstudent',
        ]

        manager_permissions = []

        for model_name in manager_models:
            actions = (
                ['view']
                if model_name == 'auditlog'
                else ['view', 'add', 'change']
            )

            for action in actions:
                permission = Permission.objects.get(
                    content_type__app_label='portal',
                    content_type__model=model_name,
                    codename=f'{action}_{model_name}',
                )
                manager_permissions.append(permission)

        manager_group.permissions.set(manager_permissions)

        self.stdout.write(
            f'LPK Managers group permissions: '
            f'{len(manager_permissions)} assigned'
        )

        # ========================================================
        # EXAM RULES
        # ========================================================

        exam_rules = [
            ('JFT_A2', 'JFT A2'),
            ('JLPT_N4', 'JLPT N4'),
            ('SSW', 'SSW Skill Exam'),
        ]

        for code, name in exam_rules:
            obj, created = ExamRule.objects.get_or_create(
                code=code,
                defaults={'name': name},
            )

            self.stdout.write(
                f'{name}: {"created" if created else "exists"}'
            )

        # ========================================================
        # JOB TYPES
        # ========================================================

        job_types = [
            'Doboku',
            'Kenchiku',
            'Lifeline',
        ]

        for name in job_types:
            obj, created = JobType.objects.get_or_create(
                name=name
            )

            self.stdout.write(
                f'{name}: {"created" if created else "exists"}'
            )

        # ========================================================
        # DOCUMENT REQUIREMENTS
        # ========================================================

        docs = [
            # GENERAL — all pathways
            ('PASSPORT', 'Passport', '旅券', ''),
            ('PHOTO', 'Photo', '写真', ''),
            ('KARTU_KELUARGA', 'Kartu Keluarga', '', ''),
            ('KTP', 'KTP', '', ''),
            ('JFT_A2_2', 'JFT A2.2', '', ''),
            ('SSW_TG_DOCUMENT', 'SSW TG Document', '', ''),
            ('MCU', 'Medical Check-Up', '', ''),

            # INTERNSHIP
            ('CHECKLIST', 'Checklist docs', '必要書類チェックリスト', ''),
            ('FORM_1_3', 'CV', '技能実習生の履歴書', 'Form 1-3'),
            ('FORM_1_10', 'LPK undertaking', '技能実習計画の認定に関する取次送出機関の誓約書', 'Form 1-10'),
            ('FORM_1_14_UNSIGNED', 'Employment contract - unsigned', '雇用契約書及び雇用条件書', 'Form 1-14 (unsigned)'),
            ('FORM_1_14_SIGNED', 'Employment contract - signed', '雇用契約書及び雇用条件書', 'Form 1-14 (signed)'),
            ('FORM_1_19', 'Facilities and benefits list', '技能実習の期間中の待遇に関する重要事項説明書', 'Form 1-19'),
            ('FORM_1_20', 'Candidate declaration', '技能実習生の申告書', 'Form 1-20'),
            ('FORM_1_23', 'Form 1-23 signed', 'Form 1-23', ''),
            ('FORM_1_27', 'Experience statement', '同種業務従事経験等説明書', 'Form 1-27'),
            ('FORM_1_28', 'Overseas organization statement', '外国の所属機関による説明書', 'Form 1-28'),
            ('FORM_1_29', 'Pre-entry training undertaking', '入国前講習実施（予定）表に関する申請者等の誓約書', 'Form 1-29'),
            ('FORM_1_39', 'Personal data consent', '技能実習生の個人情報の取扱いに係る同意書', 'Form 1-39'),
            ('SENDING_ORG', 'Sending organization undertaking', '送り出し機関との誓約書', ''),
            ('KEMENAKER', 'Kemenaker recommendation', 'Rekomendasi Kemenaker', ''),
            ('TRANSLATED_KARTU_KELUARGA', 'Translated Kartu Keluarga', '', ''),
            ('SUPPORT_CERTIFICATION', 'Support Certification', '', ''),
        ]

        document_classifications = {
            # GENERAL — all pathways
            'PASSPORT': ('GENERAL', 'STUDENT_PROVIDED'),
            'PHOTO': ('GENERAL', 'STUDENT_PROVIDED'),
            'KARTU_KELUARGA': ('GENERAL', 'STUDENT_PROVIDED'),
            'KTP': ('GENERAL', 'STUDENT_PROVIDED'),
            'JFT_A2_2': ('GENERAL', 'STUDENT_PROVIDED'),
            'SSW_TG_DOCUMENT': ('GENERAL', 'STUDENT_PROVIDED'),
            'MCU': ('GENERAL', 'STUDENT_PROVIDED'),

            # INTERNSHIP — staff prepared
            'CHECKLIST': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_10': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_14_SIGNED': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_14_UNSIGNED': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_19': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_20': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_27': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_28': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_29': ('INTERNSHIP', 'STAFF_PREPARED'),
            'FORM_1_39': ('INTERNSHIP', 'STAFF_PREPARED'),
            'SENDING_ORG': ('INTERNSHIP', 'STAFF_PREPARED'),
            'TRANSLATED_KARTU_KELUARGA': ('INTERNSHIP', 'STAFF_PREPARED'),
            'SUPPORT_CERTIFICATION': ('INTERNSHIP', 'STAFF_PREPARED'),

            # INTERNSHIP — external preparation/process
            'FORM_1_3': ('INTERNSHIP', 'EXTERNAL_PREPARATION'),
            'FORM_1_23': ('INTERNSHIP', 'EXTERNAL_PROCESS'),
            'KEMENAKER': ('INTERNSHIP', 'EXTERNAL_PROCESS'),
        }

        for code, name, jp, ref in docs:
            applicability, handling = document_classifications[code]

            obj, created = DocumentRequirement.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'japanese_name': jp,
                    'form_reference': ref,

                    # Keep legacy and current classification synchronized.
                    'pathway': applicability,
                    'applicability': applicability,

                    'handling': handling,
                    'required': True,
                    'active': True,
                },
            )

            self.stdout.write(
                f'{code}: {"created" if created else "updated"}'
            )
