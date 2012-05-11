from Products.CMFCore.utils import getToolByName
import logging
from Products.Five.browser import BrowserView


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
