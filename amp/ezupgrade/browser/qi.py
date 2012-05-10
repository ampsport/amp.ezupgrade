from Products.CMFPlone import PloneMessageFactory as _
from zope.component import getMultiAdapter
import logging
from Products.Five.browser import BrowserView


class ManageProductsView(BrowserView):
    """
    Activate and deactivate products in mass, and without weird
    permissions issues
    """

    def __call__(self):
        return self.index()

