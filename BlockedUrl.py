class BlockedUrl():
    def __init__(self, url_name, ip, is_active):
        self.url_name = url_name
        self.ip = ip
        self.is_active = is_active

    def __eq__(self, other):
        return self.ip == other.ip

    def __hash__(self):
        return hash(self.ip)
