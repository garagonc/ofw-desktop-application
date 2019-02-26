#import python_http_client
#import http as example
#import urllib.request as http
import http.client as http
import logging, os




logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
import ast


class Http:

    def __init__(self, host_info):
        #print("host_info" + str(host_info))
        self.conn = http.HTTPConnection(str(host_info["host"]), str(host_info["port"]))
        self.payload=""
        self.headers=""
        self.request=""
        self.endpoint=""


    def send_request(self, request, endpoint, payload, headers):
        self.payload=payload
        self.header=headers
        self.request=request
        self.endpoint= endpoint

        logger.debug("Sending request ")
        self.conn.request(self.request,self.endpoint, self.payload, self.header)

        res = self.conn.getresponse()
        data = res.read()
        data=ast.literal_eval(data.decode("utf-8"))
        return data

    def send_request_model_read(self, request, endpoint, payload, headers):
        self.payload=payload
        self.header=headers
        self.request=request
        self.endpoint= endpoint

        logger.debug("Sending request ")
        self.conn.request(self.request,self.endpoint, self.payload, self.header)

        res = self.conn.getresponse()
        data = res.read()
        return data

    def send_request_add(self, request, endpoint, payload, headers):
        self.payload=payload
        self.header=headers
        self.request=request
        self.endpoint= endpoint

        logger.debug("Sending request ")
        self.conn.request(self.request,self.endpoint, self.payload, self.header)

        res = self.conn.getresponse()
        #logger.debug("Response reason: " + str(res.getheader("Location")))
        header=""
        if res.getheader("Location"):
            header=res.getheader("Location")
            path=os.path.split(header)
            header = path[1]
        data = res.read()
        data=ast.literal_eval(data.decode("utf-8"))
        if header:
            return header
        else:
            return data
