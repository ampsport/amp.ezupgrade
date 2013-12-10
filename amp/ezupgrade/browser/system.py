from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component.hooks import setSite
from qi import ManageProductsView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as _
from OFS.interfaces import IApplication
import logging
import transaction


class UpgradeProductsForSite(grok.View):
    """
    Run all available upgrades for a site
    """

    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')
    grok.name('run_upgrades')

    def upgrade(self):
        """
        Find all packages in a site that need upgrades, and run them
        """
        qi = ManageProductsView(self.context, self.request)
        upgrades = qi.get_addons(apply_filter='upgrades').values()
        num_upgrades = 0
        for upgrade in upgrades:
            logging.debug("Attempting to upgrade %s" % upgrade['id'])
            if qi.upgrade_product(upgrade['id']):
                num_upgrades += 1
            else:
                logging.error("Error upgrading %s" % upgrade['id'])
        return num_upgrades

    def render(self):
        upgrades = self.upgrade()
        messages = IStatusMessage(self.request)
        messages.addStatusMessage(_(u'Upgraded %s products!' % upgrades),
                                      type="info")


class UpgradeProductsForAllSites(grok.View):
    """
    Run all available upgrades for all plone sites in this zope instance
    """

    grok.context(IApplication)
    grok.require('zope2.ViewManagementScreens')
    grok.name('up2date')

    def render(self):
        """
        look through all the plone sites, and run upgades on those sites
        returns the number of sites that were upgraded
        """
        upgraded = 0
        for child in self.context.getChildNodes():
            if getattr(child, 'portal_type', None) == 'Plone Site':
                logging.debug("Running all upgrades for %s..." % child.id)
                try:
                    transaction.begin()
                    setSite(child)
                    view = UpgradeProductsForSite(child, self.request)
                    view.upgrade()
                    transaction.get().note("Running all upgrades")
                    transaction.commit()
                    upgraded += 1
                except Exception, e:
                    logging.error("Exception upgrading %s: %s" % (child.id, e))
                except:
                    logging.error("Unknown error upgrading %s" % child.id)
        return upgraded
