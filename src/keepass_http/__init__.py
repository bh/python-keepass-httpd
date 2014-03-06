import mimetypes

# register keepass mimetypes
mimetypes.add_type("application/x-keepass-database-v1", ".kdb")
mimetypes.add_type("application/x-keepass-database-v2", ".kdx")
