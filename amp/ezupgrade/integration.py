from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implements


class NonInstallablePackages(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [u'amp.ezupgrade:uninstall']
