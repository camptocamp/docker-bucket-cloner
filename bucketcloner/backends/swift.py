import swiftclient

class Swift(object):
    def __init__(self, **kwargs):
        self.client = swiftclient.client.Connection(**kwargs)

    def list_buckets(self):
        buckets = []
        for container in self.client.get_container("")[1]:
            buckets.append(container['name'])
        return buckets
