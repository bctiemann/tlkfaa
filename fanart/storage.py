from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ManifestStaticFilesStorageNonStrict(ManifestStaticFilesStorage):

    manifest_strict = False
