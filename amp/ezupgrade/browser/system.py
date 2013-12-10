from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component.hooks import setSite
from qi import ManageProductsView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as _
from OFS.interfaces import IApplication
from Products.Five.browser import BrowserView
import logging
import transaction


def getPloneSites(context):
    for child in context.getChildNodes():
        if getattr(child, 'portal_type', None) == 'Plone Site':
            yield child


class RecookResources(BrowserView):
    """
    Go through all of the plone sites and recook the
    registries
    """
    def __call__(self):
        """
        config = getConfiguration()
        if config.debug_mode:
            return
        """
        logging.info("Recooking registries...")
        for child in getPloneSites(self.context):
            logging.info("Recooking %s" % child.id)
            resources = ['portal_javascripts', 'portal_css']
            for resource in resources:
                tool = child.get(resource)
                tool.cookResources()

        return "Order up!"


class RunPloneUpgrades(BrowserView):
    """
    Go through all of the plone sites and run any plone
    upgrades that are pending
    """
    def __call__(self):
        logging.info("Running plone upgrades...")
        upgrades = 0
        for site in getPloneSites(self.context):
            setSite(site)
            logging.info("Running Plone upgrades for %s..." % site.id)
            pm = getattr(site, 'portal_migration')
            try:
                transaction.begin()
                pm.upgrade(dry_run=False,)
                transaction.commit()
                upgrades += 1
            except Exception, e:
                transaction.abort()
                logging.error("Could not run plone upgrades for %s: %s" %(site.id, e))
            except:
                transaction.abort()
                logging.error("Unknown error running plone upgrades for %s" % site.id)
        return upgrades


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
