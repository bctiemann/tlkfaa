# tlkfaa
The Lion King Fan-Art Archive is a community art site that has been in formal existence since 1999.
Its purpose is to allow fans of Disney's *The Lion King* to create and share their art, through a number of
innovative collaborative features.

## History ##
Prior to the creation of the TLKFAA proper (with its own subdomain at https://fanart.lionking.org), the Image Archive section
of The Lion King WWW Archive (http://lionking.org) contained a "fan-art" section, featuring the work of one or two dozen 
artists. The pages of this site were manually edited into static HTML.

The first generation of the TLKFAA, created in 1999, was written in Perl, and underwent at least two major front-end
facelifts before it became clear that the amount of traffic and content the site was sustaining merited a complete rewrite
and reorganization of the data structure. The most significant rewrite in this era took place in January 2006, when the
site's general layout and design was made more or less into what it is today, from a general navigation standpoint.

In 2010 the site was rebuilt from the ground up using Java/JSP. This new design featured a completely rewritten 
jQuery-based front-end, as well as a mildly restructured database schema that addressed one glaring flaw in the original
site's design: the decision to have "artists" and "users" as their own separate, incompatible concepts. "Artists" were
users who contributed art and had a gallery page; "users" were simply profiles that allowed users to follow and favorite
content. An artist had to be linked to a user account, and this linking process was far from elegant or foolproof. Now,
however, though both tables remained present in the database, the front-end workflow for managing the "linking" behavior
and any visible manifestation of the distinction between artists and users was removed.

This 2010 rewrite was not rolled out, however, due to shifted priorities; and the 2006 design remained in force until 2016,
when the JSP site was finally made live. By this time traffic to the TLKFAA had dropped off steadily to a fraction of its
former size, and even though many of the secondary features had not been fully completed, it proved to be much faster
and more stable than the previous Perl version.

However, the front-end, which had looked forward-thinking in 2010, now seemed archaic. Furthermore, while JSP and 
JSTL/EL allowed for a much better development pattern than the ad-hoc Perl CGI scripts from the 2006 version, it still
remained an opaque and unmanageable mess compared to modern web development frameworks with support for console environments,
ORMs, static file management, and proper MVC-style separation of concerns.

So yet another total rewrite took place and was rolled out in 2018, this time in Django/Python. The new system attempts
to follow modern best practices and Django design patterns, with the bulk of the core functionality built into reusable
components in the data model layer. Logging is much improved, security is industry-standard (and the "artist"/"user"
distinction is now completely erased), and the built-in Django Admin provides out-of-the-box maintenance functionality 
that was patently unavailable in the stacks used for the previous designs.

Most especially, Django allows the site for the first time to be built around the modern development pattern of a local
dev environment, a central code repo, and one or more staging/production instances to which code can be deployed via 
a CI/CD pipeline. The TLKFAA can now be cloned to a local dev workstation and set up using familiar Django setup methods,
and is no longer anchored to its one and only production instance.

The future of the TLKFAA community might be one in which interest in the subject matter continues to slowly wane; but
the TLKFAA's purpose as a learning platform and a place to establish and implement industry best practices can now be
fully realized.

## Setup ##
