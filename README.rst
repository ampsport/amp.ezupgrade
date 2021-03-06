.. contents::

Introduction
============
This product attempts to remove a lot of the steps when creating 
upgrade steps based on profiles. It starts by combinging the task 
of creating profiles and registering as upgrade steps, and also 
makes a fair amount of assumptions to make it very easy to add new 
profiles. 


Running upgrade
===============
Just adding the product to your buildout will give you access to 
the zcml directives for upgrade steps. If you want extra features, 
you can install amp.ezupgrade into your site.

If you install the actual amp.ezupgrade product, you get a few 
things. A new quick installer which handle mass upgrades. There is
also a script the runs all upgrades from each plone site at 
/mysite/@@run_upgrades and then a script which runs all upgrades for all 
sites in a zope instance at /@@up2date. This script can also be run 
from the command line::

    ./bin/instance run src/amp.ezupgrade/scripts/up2date.py 

Still TODO here is to check for failure on any sites and abort if one 
goes awry. or at least have a switch.


Uaing Latest
============
In addition to below, I reommend using the 'latest' keyword that is 
built into CMFPlone in metadata.xml instead of the version number. It 
will automatically increment the profile number available for upgrade 
to be the highest one on the system. It just saves one more step.


Writing Upgrade Steps
=====================

Before
------
Registering an upgrade step profile involves the following::

 * Create a directory to have all of the steps (e.g. 2to3/)
 * Update the base default profile, then add the changed xml
   to that directory. It would look something like::
    /2to3
         /jsregistry.xml
         /import_steps.xml
         /catalog.xml

    /3to4   
         /viewlets.xml

    etc...

 * Register the profile of the upgrade as::
   
    <genericsetup:registerProfile
        name="2to3"
        title="Do this thing"
        description=""
        directory="profiles/2to3"
        for="Products.CMFPlone.interfaces.IMigratingPloneSiteRoot"
        provides="Products.GenericSetup.interfaces.EXTENSION"
        />

 * Register the upgrade step as a profile::
      
   <genericsetup:upgradeStep
      source="1"
      destination="2"
      title="Add simple profile viewlet"
      description=""
      handler=".upgrade1to2"
      profile="my.product:default"
      />
  
 * Add the handler, upgrade1to2, to make sure that the right
   profile is being run::

   from Products.CMFCore.utils import getToolByName
   from plone.app.upgrade.utils import loadMigrationProfile

   def upgrade1to2(context):
       loadMigrationProfile(context, 'profile-my.product.upgrades:1to2')

This is insane in a million ways, and definitely doesn't scale. This product
aims to make these things easier, step by step.

After
-----

You can either add amp.ezuprade as an egg to your buildout, or 
make it a required product in the setup.py of your egg. I suggest 
the latter because the syntax of your zcml files will depend on it.

You can start using as soon as you add the following line to a zcml 
file::

   <include package="amp.ezupgrade" file="meta.zcml" />

This line must be loaded at some point before using the new directive. 
After that, you are golden.

If you want to skip a lot of lines, leaving items blank choses 
convention over configuration::

    <genericsetup:registerUpgradeProfile
      title="Add new Javascript dependencies"
      source="2"
      destination="3"
      profile="my.package:default"
     />

You can even skip Title. 

The directory is assumed to  be profiles/<source>_to_<destination>.
<source>_to_<destination> will be the default name. The assumption 
is that you are working with an extension profile and that it will 
be attached to the plone site migration interface. You may override
as much or as little as you like.

The most verbose way of adding a profile::

   <genericsetup:registerUpgradeProfile
        name="2to3"
        title="Add new Javascript dependencies"
        description="This will include bootstrap, as well as google api"
        directory="profiles/2to3"
        for="Products.CMFPlone.interfaces.IMigratingPloneSiteRoot"
        provides="Products.GenericSetup.interfaces.EXTENSION"
        source="1"
        destination="2"
        handler="my.package.upgrade1to2"
        profile="my.package:default"
        />


Recommended Setup
-----------------
In your products base directory, create another folder called 
"upgrades". The layout would then most likely look like this::

    /profiles
       /default
       /uninstall
    /upgrades
       /profiles
       __init__.py  # this is a package
       configure.zcml  # all new stuff goes here
       setuphandlers.py  # if you want it to do fancy stuff

Then make sure to register that folder in the root configure.zcml::

    <include package=".upgrades" />


In your upgrades folder, you will need a configure.zcml, and then 
you can start to list your profile folders from there.  In the 
configure.zcml, you can list your upgrades with the syntax indicated
above. 

After a few upgrades, the setup would start to look like::

    /profiles
       /default
       /uninstall
       /upgrades
           configure.zml
           /2to3
               jsregistry.xml
               import_steps.xml
               catalog.xml
           /3to4   
               viewlets.xml
          


And you configure.zcml will look like::

   <configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:genericsetup="http://namespaces.zope.org/genericsetup"> 

    <include package="amp.ezupgrade" file="meta.zcml"/>

    <genericsetup:registerUpgradeProfile
      title="Remove search in context"
      source="2"
      destination="3"
      profile="my.product:default"
     />
    <genericsetup:registerUpgradeProfile
      title="Add new viewlet for pants"
      source="3"
      destination="4"
      profile="my.product:default"
     />
    </configure>


Holy Moly
---------
That's what I said. This is still a decent amount of typing to 
be done but at least it cuts out a lot of typing and after initial 
setup it gets hella easier.  


TODO
----
- Support higher level directories a la 

<genericsetup:registerUpgradeFolder
   directory="profiles"
   profile="amp.base:default">

   <genericsetup:registerUpgradeProfile
        title="DO THIS THING"
        source="1"
        destination="2"
        />
</genericsetup:registerUpgradeFolder>

- support non sequential upgrades

