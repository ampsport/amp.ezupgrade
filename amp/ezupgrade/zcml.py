
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.interface import Interface
import zope.schema
import zope.configuration
from Products.CMFPlone.interfaces import IMigratingPloneSiteRoot
from Products.GenericSetup.upgrade import UpgradeStep
from Products.GenericSetup.zcml import _registerUpgradeStep
from Products.GenericSetup.interfaces import EXTENSION
from Products.GenericSetup.registry import _profile_registry


class IRegisterUpgradeProfileDirective(Interface):

    """
    Register upgrade profiles. The combination of an upgrade step
    and a generic setup profile. In the backend it will be registered
    as both.

    Notes: name will be source_to_destination
    """
    name = PythonIdentifier(
        title=u'Name',
        description=u"If not specified <source>_to_<destination> is used.",
        default=None,
        required=False)

    title = MessageID(
        title=u'Title',
        description=u'Optional title for the profile.',
        default=None,
        required=False)

    description = MessageID(
        title=u'Description',
        description=u'Optional description for the profile.',
        default=None,
        required=False)
    # we will leave this out
    directory = Path(
        title=u'Path',
        description=u"If not specified 'profiles/<name>' is used.",
        required=False)

    provides = GlobalObject(
        title=u'Type',
        description=u"If not specified 'EXTENSION' is used.",
        default=EXTENSION,
        required=False)

    for_ = GlobalObject(
        title=u'Site Interface',
        description=u'If not specified the profile is available for migration.',
        default=IMigratingPloneSiteRoot,
        required=False)

    source = zope.schema.ASCII(
        title=u"Source version",
        description=u'If not specific, * will be used',
        required=True)

    destination = zope.schema.ASCII(
        title=u"Destination version",
        description=u'If not specific, 0 will be used. Please leave source and dest empty to do the first upgrade',
        required=True)

    # XXX WTF is this?
    sortkey = zope.schema.Int(
        title=u"Sort key",
        required=False)

    profile = zope.schema.TextLine(
        title=u"GenericSetup profile id",
        required=True)

    handler = GlobalObject(
        title=u"Upgrade handler",
        required=False)

    checker = GlobalObject(
        title=u"Upgrade checker",
        required=False)


def registerUpgradeProfile(_context, name=None, title=None,
                           description=None,
                           directory=None, provides=EXTENSION,
                           for_=IMigratingPloneSiteRoot,
                           source=None, destination=None,
                           sort_key=None, profile=None,
                           handler=None, checker=None):

    product = _context.package.__name__
    if directory is None:
        directory = 'profiles/%s' % name

    if description is None:
        description = u''

    if not source:
        source = '*'

    if not destination:
        destination = '0'

    if name is None:
        name = '%s %s' % (source, destination)

    if title is None:
        title = u"Profile '%s' from '%s'" % (name, product)

    if not handler:
        # TODO: default handler
        pass

    _context.action(
        discriminator=('registerUpgradeProfile', product, name),
        callable=_registerUpgradeProfile,
        args=(name, title, description, directory, product, provides, for_,
              profile, source, destination, handler, sort_key, checker)
        )


def _registerUpgradeProfile(name, title, description, directory, product,
                            provides, for_, profile,
                            source, destination, handler,
                            sortkey, checker):
    _profile_registry.registerProfile(name, title, description, directory,
                                      product, provides, for_)
    step = UpgradeStep(title, profile, source, destination, description,
                       handler, checker, sortkey)

    _registerUpgradeStep(step)

