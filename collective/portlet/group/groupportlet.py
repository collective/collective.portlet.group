import logging
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile as VPTF
from collective.portlet.group import GroupPortletMessageFactory as _

from zope.app.form.browser.textwidgets import TextWidget
from Products.CMFCore.utils import getToolByName

class GroupTextWidget(TextWidget):

    def __init__(self, *args):
        super(GroupTextWidget, self).__init__(*args)

    datatable = VPTF('datatable.pt')

    def __call__(self):
        return self.datatable()

    def getGroups(self):
        acl_users = getToolByName(self.context.context, 'acl_users')
        groups = acl_users.searchGroups()
        def getGroupInfo(group):
            return {'id':group['id'],
                    'title':group['title']
                    }
        return [getGroupInfo(group) for group in groups]

    def normalizeGroupId(self, groupid):
        ret = groupid
        try:
            ret = unicode(ret)
        except Exception, e:
            ret = unicode(ret.decode('utf-8'))
        return ret


class IGroupPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    group   = schema.TextLine(title=_(u"Group"),
                                  description=_(u"Select the group"),
                                  required=True)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGroupPortlet)

    group = u""

    def __init__(self, group=u""):
        self.group = group

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Group "


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('groupportlet.pt')

    def getMembers(self):
        """ get the contact informations the portlet is pointing to"""
        logger = logging.getLogger('collective.portlet.group.groupportlet.Renderer.getMembers')
        gtool = getToolByName(self.context, 'portal_groups')
        mtool = getToolByName(self.context, 'portal_membership')
        groupid = self.data.group

        if not groupid:
            return ()

        def getMInfo(m):
            info = {}
            member = mtool.getMemberById(m)
#            info['email'] = member.getProperty("email")
            if member is None:
                logger.warn(
                    'Memberdata for %s (group: %s)  '
                    'are unavailable' % (m, groupid)
                )
            return member

        gmembers = []
        try:
            gmembers = gtool.getGroupMembers(groupid)
        except UnicodeDecodeError:
            gmembers = gtool.getGroupMembers(
                groupid.encode('utf-8'))

        members = filter(
            lambda x:x is not None,
            [getMInfo(m) for m in gmembers]
        )

        return members

    def mailtogroup(self):
        """ return the href with a mailto: all the group members"""
        members = self.getMembers()
        emails = [m.getProperty('email') for m in members]
        return 'mailto:' + ';'.join(emails)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IGroupPortlet)
    form_fields['group'].custom_widget = GroupTextWidget

    label = _(u"title_add_group_portlet",
              default=u"Add group portlet")

    def setUpWidgets(self, ignore_request=False):
        super(AddForm, self).setUpWidgets(ignore_request=ignore_request)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IGroupPortlet)
    form_fields['group'].custom_widget = GroupTextWidget

    label = _(u"title_edit_group_portlet",
              default=u"Edit group portlet")

    def setUpWidgets(self, ignore_request=False):
        super(EditForm, self).setUpWidgets(ignore_request=ignore_request)
