from zope.i18nmessageid import MessageFactory
GroupPortletMessageFactory = MessageFactory('collective.portlet.group')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
