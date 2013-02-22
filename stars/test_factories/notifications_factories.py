import factory

from stars.apps.notifications.models import EmailTemplate, CopyEmail


class EmailTemplateFactory(factory.Factory):
    FACTORY_FOR = EmailTemplate

    slug = factory.Sequence(lambda i: 'slug-{0}'.format(i))


class CopyEmailFactory(factory.Factory):
    FACTORY_FOR = CopyEmail

    template = factory.SubFactory(EmailTemplateFactory)
