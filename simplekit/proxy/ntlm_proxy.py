import httplib
import socket

import requests
import requests.packages.urllib3.connection as urllib3_connection
import requests.packages.urllib3.connectionpool as urllib3_connection_pool
from ntlm import ntlm

__author__ = 'benjamin.c.yan'


class NTLMHTTPConnection(requests.packages.urllib3.connection.HTTPConnection):
    Domain = None
    UserName = None
    Password = None

    def connect(self):
        super(NTLMHTTPConnection, self).connect()
        self._authenticate()

    def _output(self, s):
        if not self._buffer:
            self._http_line = s + '\r\n'

        if s.startswith('Host:'):
            self._http_line += s + '\r\n'

        super(NTLMHTTPConnection, self)._output(s)

    def _send_authenticate(self, line, authorization):
        self.sock.sendall(line)
        self.sock.sendall(authorization)
        self.sock.sendall('Proxy-Connection: keep-alive\r\n')
        self.sock.sendall('Connection: keep-alive\r\n')
        self.sock.sendall('\r\n')

    def _authenticate(self):
        domain, username, password = self.Domain, self.UserName, self.Password

        line = self._http_line
        del self._http_line
        authorization = "Proxy-Authorization: %s\r\n" % 'NTLM %s' % ntlm.create_NTLM_NEGOTIATE_MESSAGE(
            "%s\\%s" % (domain, username))

        self._send_authenticate(line, authorization)

        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        response.begin()

        if response.status == httplib.PROXY_AUTHENTICATION_REQUIRED:
            _ = response.read()
            auth_header_value = response.getheader('proxy-authenticate')
            server_challenge, negotiate_flags = ntlm.parse_NTLM_CHALLENGE_MESSAGE(auth_header_value[5:])

            # build response
            auth = 'NTLM %s' % ntlm.create_NTLM_AUTHENTICATE_MESSAGE(server_challenge, username, domain, password,
                                                                     negotiate_flags)
            self._send_authenticate(line, "%s: %s\r\n" % ('Proxy-Authorization', auth))

            response = self.response_class(self.sock, strict=self.strict,
                                           method=self._method)
            response.begin()
            _ = response.read()

            if response.status != httplib.OK:
                self.close()
                raise socket.error("Tunnel connection failed: %d %s" % (response.status, response.reason))


class NTLMHTTPSConnection(urllib3_connection.HTTPSConnection):
    Domain = None
    UserName = None
    Password = None

    def _tunnel(self):
        # TODO(benjamin): hard code, need get domain, username, password from configuration
        domain, username, password = self.Domain, self.UserName, self.Password

        self._set_hostport(self._tunnel_host, self._tunnel_port)
        self.send("CONNECT %s:%d HTTP/1.0\r\n" % (self.host, self.port))
        self.send("%s: %s\r\n" % (
            'Proxy-Authorization', 'NTLM %s' % ntlm.create_NTLM_NEGOTIATE_MESSAGE("%s\\%s" % (domain, username))))
        for header, value in self._tunnel_headers.iteritems():
            self.send("%s: %s\r\n" % (header, value))
        self.send("\r\n")
        response = self.response_class(self.sock, strict=self.strict,
                                       method=self._method)
        response.begin()

        if response.status == httplib.PROXY_AUTHENTICATION_REQUIRED:
            auth_header_value = response.getheader('proxy-authenticate')
            server_challenge, negotiate_flags = ntlm.parse_NTLM_CHALLENGE_MESSAGE(auth_header_value[5:])

            # build response
            auth = 'NTLM %s' % ntlm.create_NTLM_AUTHENTICATE_MESSAGE(server_challenge, username, domain, password,
                                                                     negotiate_flags)
            self.send("CONNECT %s:%d HTTP/1.0\r\n" % (self.host, self.port))
            self.send("%s: %s\r\n" % ('Proxy-Authorization', auth))
            for header, value in self._tunnel_headers.iteritems():
                self.send("%s: %s\r\n" % (header, value))
            self.send("\r\n")
            response = self.response_class(self.sock, strict=self.strict,
                                           method=self._method)
            response.begin()

            if response.status != httplib.OK:
                self.close()
                raise socket.error("Tunnel connection failed: %d %s" % (response.status,
                                                                        response.reason))
