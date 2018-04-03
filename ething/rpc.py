import socket
import struct
import pickle
import os
import tempfile
import traceback


class RPC_Response(object):
    
    def __init__(self, result = None, exception = None, args = None, kwargs = None, async = False, traceback = None):
        self.result = result
        self.args = args
        self.kwargs = kwargs
        self.exception = exception
        self.async = async
        self.traceback = traceback

class RPC_Request(object):
    
    def __init__(self, func, args, kwargs, response = True):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.response = response

class RPC_Sub(object):
    
    def __init__(self, topic):
        self.topic = topic

class RPC_Pub(object):
    
    def __init__(self, topic, message):
        self.topic = topic
        self.message = message

class RPC_pubsubmsg(object):
    
    def __init__(self, topic, message):
        self.topic = topic
        self.message = message


default_address = os.path.join(tempfile.gettempdir(), './ething_socket')


class RPC(object):
    
    _cmds = {}
    
    def __init__(self, core, address = default_address):
        self.core = core
        self.log = core.log
        self._address = address
        
        self.log.debug("RPC initiated, address = %s" % str(address))
    
    @property
    def address (self):
        return self._address
    
    
    def start_server(self, manager):
        
        if isinstance(self._address, basestring):
            
            # Make sure the socket does not already exist
            try:
                os.unlink(self._address)
            except OSError:
                if os.path.exists(self._address):
                    raise
        
        server = RPC_Server(self, manager)
        
        server.start()
        
        return server
        
    
    def _send_obj(self, sock, obj):
        data = pickle.dumps(obj)
        try:
            sock.sendall(struct.pack('!i', len(data)))
            sock.sendall(data)
        except:
            pass
    
    
    def _read_obj(self, sock):
        header = sock.recv(4)
        if len(header) == 0:
            return None
        
        size = struct.unpack('!i', header)[0]
        data = sock.recv(size)
        if len(data) != size:
            return None
        
        return pickle.loads(data)
    
    def _create_socket(self):
        if isinstance(self._address, basestring):
            address_family = socket.AF_UNIX
        else:
            address_family = socket.AF_INET
        
        sock = socket.socket(address_family, socket.SOCK_STREAM)
        
        return sock
    
    def _open_socket(self):
        
        sock = self._create_socket()
        
        try:
            sock.settimeout(0.1)
            sock.connect(self._address)
            sock.settimeout(None)
        except socket.error as e:
            self.log.error("RPC connect error : %s" % str(e))
            raise
        
        return sock
    
    def request(self, func, *args, **kwargs):
        """
        execute a function on the server and return synchronously the response
        """
        sock = self._open_socket()
        
        req = RPC_Request(func, args, kwargs)
        
        self._send_obj(sock, req)
        
        resp = self._read_obj(sock)
        
        sock.close()
        
        if resp.exception is not None:
            if resp.traceback:
                raise type(resp.exception)(resp.exception.message + ' , traceback: %s' % resp.traceback)
            else:
                raise resp.exception
        
        if resp.async:
            if resp.kwargs:
                return (resp.args, resp.kwargs)
            else:
                return resp.args
        else:
            return resp.result
    
    def send(self, func, *args, **kwargs):
        """
        execute a function on the server, do not wait any response
        """
        sock = self._open_socket()
        req = RPC_Request(func, args, kwargs, response = False)
        self._send_obj(sock, req)
        sock.close()
    
    def subscribe(self, topic):
        """
        subscribe to a topic and start listening for message
        """
        
        client = RPC_SubClient(self, topic)
        client.start()
        
        return client
    
    def publish(self, topic, message):
        """
        publish a message to a topic
        """
        sock = self._open_socket()
        
        req = RPC_Pub(topic, message)
        
        self._send_obj(sock, req)
        
        sock.close()
    
    
    @classmethod
    def register(cls, key, func, callback_name = None):
        cls._cmds[key] = (func, callback_name)
    
    @classmethod
    def unregister(cls, key):
        if key in cls._cmds:
            del cls._cmds[key]
    
    

class RPC_SubClient(object):
    
    def __init__(self, rpc, topic):
        self.rpc = rpc
        self.log = rpc.log
        self.topic = topic
        self.sock = None
    
    def start(self):
        if self.sock is not None:
            raise Exception('a socket is already opened')
        
        self.sock = self.rpc._open_socket()
        req = RPC_Sub(self.topic)
        self.rpc._send_obj(self.sock, req)
        
        self.log.debug("start sub topic=%s" % self.topic)
    
    def stop(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            self.log.debug("stop sub topic=%s" % self.topic)
    
    def get(self):
        """
        wait until a message arrive
        """
        resp = self.rpc._read_obj(self.sock)
        
        if resp is None:
            self.log.debug("rpc server disconnected")
            self.stop()
            return
        
        self.log.debug("msg received topic=%s data=%s" % (resp.topic, str(resp.message)))
        return resp


class RPC_Server(object):
    
    def __init__(self, rpc, manager):
        self.rpc = rpc
        self.log = rpc.log
        self.sock = None
        self.manager = manager
        self._subs = {}
        self._n = 0
    
    def start(self):
        
        if self.sock is not None:
            raise Exception('a socket is already opened')
        
        self._n = 0
        self.sock = self.rpc._create_socket()
        self.sock.setblocking(False)
        
        # Bind the socket to the port
        self.sock.bind(self.rpc.address)
        self.log.info("start RPC server on %s" % str(self.rpc.address));
        self.sock.listen(100)
        
        self.manager.registerReadSocket(self.sock, self._process)
    
    
    def stop(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            self._subs = {}
            self.log.debug("stop RPC server")
    
    def _process(self):
        # new client is connected
        self._n += 1
        client_sock, client_address = self.sock.accept()
        # self.log.debug("new RPC client connected %s (%d)" % (str(client_address),self._n) )
        
        self.manager.registerReadSocket(client_sock, self._process_client, (client_sock,))
    
    def _process_client(self, sock):
        # a client send some data
        # self.log.debug("incoming RPC client data")
        rpc = self.rpc
        req = rpc._read_obj(sock)
        
        if req is None:
            self._n -= 1
            # self.log.debug("RPC client disconnect")
            self.manager.unregisterReadSocket(sock)
            
            # remove the socket from any pub
            for topic in self._subs:
                if sock in self._subs[topic]:
                    self._subs[topic].remove(sock)
            
            return
        
        if isinstance(req, RPC_Request):
            resp = None
            
            if req.func in RPC._cmds:
                
                it = RPC._cmds[req.func]
                func = it[0]
                callback_name = it[1]
                
                if callback_name is not None and req.response:
                    # async
                    try:
                        def cb(*args, **kwargs):
                            resp = RPC_Response(args = args, kwargs = kwargs, async = True)
                            rpc._send_obj(sock, resp)
                            sock.close()
                            self._n -= 1
                            self.manager.unregisterReadSocket(sock)
                        
                        req.kwargs[callback_name] = cb
                        
                        func(*req.args, **req.kwargs)
                    except Exception as e:
                        resp = RPC_Response(exception = e, traceback = traceback.format_exc())
                    
                else:
                    # sync
                    try:
                        resp = RPC_Response(result = func(*req.args, **req.kwargs))
                    except Exception as e:
                        resp = RPC_Response(exception = e, traceback = traceback.format_exc())
            else:
                resp = RPC_Response(exception = Exception('unknown function %s' % req.func))
            
            if resp is not None:
                if req.response:
                    rpc._send_obj(sock, resp)
                sock.close()
                self._n -= 1
                self.manager.unregisterReadSocket(sock)
        
        elif isinstance(req, RPC_Sub):
            
            topic = req.topic
            
            if topic not in self._subs:
                self._subs[topic] = {
                    'sockets': []
                }
            
            self._subs[topic]['sockets'].append(sock)
            
        elif isinstance(req, RPC_Pub):
            topic = req.topic
            message = req.message
            
            if topic in self._subs:
                
                m = RPC_pubsubmsg(topic, message)
                
                for s in self._subs[topic]['sockets']:
                    if s is not sock:
                        rpc._send_obj(s, m)
        
    

if __name__ == '__main__':
    
    import sys
    import logging
    import time
    from SocketManager import SocketManager
    
    logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    class Core(object):
        log = logger
    
    
    core = Core()
    manager = SocketManager(core)
    rpc = RPC(core)
    
    
    def test0():
        
        if len(sys.argv)>1 and sys.argv[1] == 'server':
            
            def hello():
                print "execute hello()"
                return 'world'
            
            def delayed(callback):
                import threading
                print "execute delayed()"
                
                def cb():
                    callback('async result')
                
                t = threading.Timer(1.0, cb)
                t.start()
                
                return
            
            rpc.register('hello', hello)
            rpc.register('delayed', delayed, callback_name = 'callback')
            
            rpc.start_server(manager)
            manager.loop_forever()
        
        else:
            
            t0 = time.time()
            print rpc.request('hello')
            tf = time.time()
            print tf-t0
            
            t0 = time.time()
            print rpc.send('hello')
            tf = time.time()
            print tf-t0
            
            t0 = time.time()
            print rpc.request('delayed')
            tf = time.time()
            print tf-t0
            
            t0 = time.time()
            print rpc.send('delayed')
            tf = time.time()
            print tf-t0
        
    
    def test1():
        
        if len(sys.argv)>1 and sys.argv[1] == 'server':
            
            tf = time.time() + 10
            
            rpc.start_server(manager)
            
            while time.time() < tf:
                manager.loop(1)
                rpc.publish('mytopic', 'message or object %s' % str(time.time()))
        
        
        else:
            
            client = rpc.subscribe('mytopic')
            
            while True:
                message = client.get()
                if message is None:
                    break
                print message
    
    def test2():
            
        tf = time.time() + 30
        
        rpc.start_server(manager)
        
        i=0
        while time.time() < tf:
            time.sleep(0.5)
            i+=1
            print "send", i
            rpc.send('mytopic', 'message or object %s' % str(time.time()))
        
            
    
    test2()