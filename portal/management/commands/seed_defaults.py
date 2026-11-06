from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from portal.models import ExamRule, JobType, DocumentRequirement

class Command(BaseCommand):
    help = 'Create initial IJB exam rules, job types, and configurable document checklist.'
    def handle(self, *args, **options):
        staff_group, _ = Group.objects.get_or_create(name='LPK Staff')
        staff_group.permissions.clear()
        self.stdout.write(
            'LPK Staff group permissions: cleared (portal access only)'
        )

        manager_group, _ = Group.objects.get_or_create(name='LPK Managers')

        manager_models = [
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
        for code, name in [('JFT_A2','JFT A2'),('JLPT_N4','JLPT N4'),('SSW','SSW Skill Exam')]:
            obj, created = ExamRule.objects.get_or_create(code=code, defaults={'name':name})
            self.stdout.write(f'{name}: {"created" if created else "exists"}')
        for name in ['Doboku','Kenchiku','Lifeline']:
            obj, created = JobType.objects.get_or_create(name=name)
            self.stdout.write(f'{name}: {"created" if created else "exists"}')
        docs = [
            ('PASSPORT','Passport','旅券',''),('PHOTO','Photo','写真',''),('CHECKLIST','Checklist docs','必要書類チェックリスト',''),
            ('FORM_1_3','CV','技能実習生の履歴書','Form 1-3'),
            ('FORM_1_10','LPK undertaking','技能実習計画の認定に関する取次送出機関の誓約書','Form 1-10'),
            ('FORM_1_14_UNSIGNED','Employment contract - unsigned','雇用契約書及び雇用条件書','Form 1-14 (unsigned)'),
            ('FORM_1_14_SIGNED','Employment contract - signed','雇用契約書及び雇用条件書','Form 1-14 (signed)'),
            ('FORM_1_19','Facilities and benefits list','技能実習の期間中の待遇に関する重要事項説明書','Form 1-19'),
            ('FORM_1_20','Candidate declaration','技能実習生の申告書','Form 1-20'),
            ('FORM_1_27','Experience statement','同種業務従事経験等説明書','Form 1-27'),
            ('FORM_1_28','Overseas organization statement','外国の所属機関による説明書','Form 1-28'),
            ('FORM_1_29','Pre-entry training undertaking','入国前講習実施（予定）表に関する申請者等の誓約書','Form 1-29'),
            ('FORM_1_39','Personal data consent','技能実習生の個人情報の取扱いに係る同意書','Form 1-39'),
            ('SENDING_ORG','Sending organization undertaking','送り出し機関との誓約書',''),
            ('KEMENAKER','Kemenaker recommendation','Rekomendasi Kemenaker',''),
            ('FORM_1_23','Form 1-23 signed','Form 1-23',''),
        ]
        for code, name, jp, ref in docs:
            _, created = DocumentRequirement.objects.get_or_create(code=code, defaults={'name':name,'japanese_name':jp,'form_reference':ref})
            if created: self.stdout.write(f'{code}: created')
