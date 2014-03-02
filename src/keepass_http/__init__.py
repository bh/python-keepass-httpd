
import mimetypes

from keepass_http.utils import ConfDir


# register keepass mimetypes
mimetypes.add_type("application/x-keepass-database-v1", ".kdb")
mimetypes.add_type("application/x-keepass-database-v2", ".kdx")

kpconf = ConfDir()
kpconf.initialize_logging()