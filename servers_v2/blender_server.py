# pip3 install codelab_adapter_client # blender
from io import StringIO
import contextlib
import sys
import time

from codelab_adapter_client import AdapterNode
from codelab_adapter_client.utils import threaded
import bpy
from loguru import logger


class BlenderNode(AdapterNode):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim/blender"

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    def extension_message_handle(self, topic, payload):
        python_code = payload["content"]
        logger.info(f'python_code: {python_code}')
        # extension_python_kernel.py
        try:
            output = eval(python_code, {"__builtins__": None}, {
                "bpy": bpy,
            })
        except Exception as e:
            output = e
        payload["content"] = str(output)
        message = {"payload": payload}
        self.publish(message)

    def exit_message_handle(self, topic, payload):
        self.terminate()

    @threaded
    def run(self):
        while self._running:
            time.sleep(0.5)


node = BlenderNode()
node.receive_loop_as_thread()
# node.run()
