
import http.client


class Http:

    def __init__(self, host_info):
        print("host_info" + str(host_info))
        self.conn = http.client.HTTPConnection(str(host_info["-host"]), str(host_info["-port"]))
        self.payload=""
        self.headers=""
        self.request=""
        self.endpoint=""


    def send_request(self, request, endpoint, payload, headers):
        self.payload=payload
        self.header=headers
        self.request=request
        self.endpoint= endpoint

        print("Sending request ")
        self.conn.request(self.request,self.endpoint, self.payload, self.header)

        res = self.conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"))
