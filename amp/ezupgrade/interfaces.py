from plone.theme.interfaces import IDefaultPloneLayer


class IAmpEzupgradeLayer(IDefaultPloneLayer):

    """This layer will be assigned to all amp.ezupgrade browser layer customizations, so that they can be
    overridden at a higher level if necessary. The layer is registered in profiles/default/browserlayer.xml
    """

