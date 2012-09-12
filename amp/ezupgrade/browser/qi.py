from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
import logging
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.GenericSetup import EXTENSION
from plone.memoize import view


class ManageProductsView(BrowserView):
    """
    Activate and deactivate products in mass, and without weird
    permissions issues
    """

    def __init__(self, *args, **kwargs):
        super(ManageProductsView, self).__init__(*args, **kwargs)
        self.qi = getToolByName(self.context, 'portal_quickinstaller')
        self.ps = getToolByName(self.context, 'portal_setup')

    def __call__(self):
        return self.index()

    @view.memoize
    def marshall_addons(self):
        addons = {}

        profiles = self.ps.listProfileInfo()
        for profile in profiles:
            if profile['type'] != EXTENSION:
                continue
            pid = profile['id']
            pid_parts = pid.split(':')
            if len(pid_parts) != 2:
                logging.error("Profile with id '%s' is invalid." % pid)
            product_id = profile['product']
            profile_type = pid_parts[-1]
            if product_id not in addons:
                # get some basic information on the product
                product_file = self.qi.getProductFile(product_id)
                installed = False
                upgrade_info = None
                p_obj = self.qi._getOb(product_id, None)
                if p_obj:
                    # TODO; if you install then uninstall, the
                    # presence lingers in the qi. Before it is
                    # run the very first time, it doesn't exist
                    # at all in the qi. How remove the qi from this?
                    installed = p_obj.isInstalled()
                    upgrade_info = self.qi.upgradeInfo(product_id)
                else:
                    # XXX: holy rabbit hole batman!
                    if not self.qi.isProductInstallable(product_id):
                        continue

                addons[product_id] = {
                            'id': product_id,
                            'title': product_id,
                            'description': '',
                            'product_file': product_file,
                            'upgrade_profiles': {},
                            'other_profiles': [],
                            'install_profile': None,
                            'uninstall_profile': None,
                            'is_installed': installed,
                            'upgrade_info': upgrade_info,
                            'profile_type': profile_type,
                            }
            product = addons[product_id]
            if profile_type == 'default':
                product['title'] = profile['title']
                product['description'] = profile['description']
                product['install_profile'] = profile
            elif profile_type == 'uninstall':
                product['uninstall_profile'] = profile
            else:
                if 'version' in profile:
                    product['upgrade_profiles'][profile['version']] = profile
                else:
                    product['other_profiles'].append(profile)
        return addons

    def get_addons(self, apply_filter=None, product_name=None):
        """
        100% based on generic setup profiles now. Kinda.
        For products magic, use the zope quickinstaller I guess.

        @filter:= 'installed': only products that are installed
                  'upgrades': only products with upgrades
                  'available': products that are not installed bit
                               could be

        @product_name:= a specific product id that you want info on. Do
                   not pass in the profile type, just the name

        XXX: I am pretty sure we don't want base profiles ...
        """
        addons = self.marshall_addons()
        filtered = {}
        for product_id, addon in addons.items():
            if product_name and addon['id'] != product_name:
                continue

            installed = addon['is_installed']
            if apply_filter in ['installed', 'upgrades'] and not installed:
                continue
            elif apply_filter == 'available':
                if installed:
                    continue
                # filter out upgrade profiles
                if addon['profile_type'] != 'default':
                    continue
            elif apply_filter == 'upgrades':
                # weird p.a.discussion integration behavior
                upgrade_info = addon['upgrade_info']
                if type(upgrade_info) == bool:
                    continue

                if not upgrade_info['available']:
                    continue

            filtered[product_id] = addon

        return filtered

    def get_upgrades(self):
        """
        Return a list of products that have upgrades on tap
        """
        return self.get_addons(apply_filter='upgrades').values()

    def get_installed(self):
        return self.get_addons(apply_filter='installed').values()

    def get_available(self):
        return self.get_addons(apply_filter='available').values()

    def upgrade_product(self, product):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        products = self.request.get('prefs_reinstallProducts', None)
        messages = IStatusMessage(self.request)
        try:
            qi.upgradeProduct(product)
            messages.addStatusMessage(_(u'Upgraded %s!' % product),
                                      type="info")
            return True
        except Exception, e:
            logging.error("Could not upgrade %s: %s" % (product, e))
            messages.addStatusMessage(_(u'Error upgrading %s.' % product),
                                      type="error")

        return False


class UpgradeProductsView(BrowserView):
    """
    Upgrade a product... or twenty
    """
    def __call__(self):
        qi = ManageProductsView(self.context, self.request)
        products = self.request.get('prefs_reinstallProducts', None)
        if products:
            for product in products:
                qi.upgrade_product(product)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/manage_products')


class InstallProductsView(BrowserView):

    def __call__(self):
        """
        Install products by running the default import steps
        XXX: is this running all profiles?
        """
        qi = getToolByName(self.context, 'portal_quickinstaller')
        setupTool = getToolByName(self.context, 'portal_setup')
        profiles = self.request.get('install_products')
        msg_type = 'info'
        if profiles:
            messages = IStatusMessage(self.request)
            for profile in profiles:
                # TODO: find out where this is and don't run already activated profiles
                setupTool.runAllImportStepsFromProfile(profile)
                msg = _(u'Installed %s!' % profile)
                messages.addStatusMessage(msg, type=msg_type)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/manage_products')


class UninstallProductsView(BrowserView):
    def __call__(self):
        # XXX: Need to call the uninstall profile
        qi = getToolByName(self.context, 'portal_quickinstaller')
        products = self.request.get('uninstall_products')
        msg_type = 'info'
        if products:
            messages = IStatusMessage(self.request)
            # 1 at a time for better error messages
            for product in products:
                try:
                    qi.uninstallProducts(products=[product, ])
                    msg = _(u'Uninstalled %s.' % product)
                except Exception, e:
                    logging.error("Could not uninstall %s: %s" % (product, e))
                    msg_type = 'error'
                    msg = _(u'Error uninstalling %s' % product)
                messages.addStatusMessage(msg, type=msg_type)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/manage_products')
