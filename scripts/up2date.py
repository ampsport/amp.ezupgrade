from Zope2 import app
from amp.ezupgrade.browser.system import UpgradeProductsForAllSites
from zope.globalrequest import getRequest


if __name__ == "__main__":    
    root = app()
    view = UpgradeProductsForAllSites(root, getRequest())
    view.render()
