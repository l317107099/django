from django.core.files.storage import Storage
# from fdfs_client.client import fdfs_client
class FDFSStorage(Storage):
    def _open(self,name,mode='rb'):
        pass

    # def _save(self,name,content):
    #     fdfs_client()
    #