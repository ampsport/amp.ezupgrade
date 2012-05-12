from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
import logging
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class ManageProductsView(BrowserView):
    """
    Activate and deactivate products in mass, and without weird
    permissions issues
    """

    def __init__(self, *args, **kwargs):
        super(ManageProductsView, self).__init__(*args, **kwargs)
        self.qi = getToolByName(self.context, 'portal_quickinstaller')

    def __call__(self):
        return self.index()

    def installable_products(self):
        return self.qi.listInstallableProducts()

    def installed_products(self):
        products = self.qi.listInstalledProducts()
        valid = []
        for product in products:
            if not product['isHidden'] and not product['isLocked']:
                valid.append(product)
        return valid

    #   security.declareProtected(ManagePortal, 'listInstalledProducts')
    def list_products(self, upgrades=True, installed=True, uninstalled=True,
                      hidden=False, locked=False, errors=False, removed=False):
        '''
        Return a list of products with all the details needed for display.

        The variables all represent items that should be included in the
        return set. Default is to return everything except for things that
        have errors, are hiddden, or are locked.

        To reuturn only items that need upgrades, for example, pass in
        upgrades = True, installed = False, and uninstalled = False

        To return all installed items that don't need upgrades, pass in
        upgrades = False, installed = True, uninstalled = False
        '''
        results = []
        candidates = self.qi.objectValues()
        for candidate in candidates:
            cid = candidate.id
            if not removed and not self.qi.isProductInstallable(cid):
                continue
            if not hidden and not candidate.isVisible():
                continue
            if not locked and candidate.isLocked():
                continue
            if not errors and candidate.hasError():
                continue

            isInstalled = candidate.isInstalled()
            upgrade_info = self.qi.upgradeInfo(cid)

            # upgrades implies installed
            if upgrades:
                if not upgrade_info['available'] and not installed:
                    continue
            else:
                if (isInstalled and not installed) or (not isInstalled and \
                                                   not uninstalled):
                    continue
            #            p = self._getOb(r,None)
            profile = self.qi.getInstallProfile(cid)
            name = cid
            description = self.qi.getProductDescription(cid)
            product_file = self.qi.getProductFile(cid)
            if profile:
                name = profile['title']
                description = profile['description']
            results.append({'id': cid,
                            'title': name,
                            'status': candidate.getStatus(),
                            'description': description,
                            'installedVersion': candidate.getInstalledVersion(),
                            'upgrade_info': upgrade_info,
                            'product_file': product_file,
                            })

        results.sort(lambda x, y: cmp(x.get('title', x.get('id')),
                                     y.get('title', y.get('id'))))
        return results


class UpgradeProductsView(BrowserView):
    """
    Upgrade a product... or twenty
    """
    def __call__(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        products = self.request.get('prefs_reinstallProducts', None)
        if products:
            for product in products:
                qi.upgradeProduct(product)
                msg = _(u'Upgraded ${product}!', mapping={'product':product})
                messages = IStatusMessage(self.request)
                messages.addStatusMessage(msg, type="info")

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/manage_products')
