import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
import evdev
import asyncio
import threading

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        device_path = '/dev/input/event13'
        self.device = evdev.InputDevice(device_path)
        self.get_logger().info(f'Connected to device: {self.device.name}')

        self.publisher_ = self.create_publisher(String, 'topic', 10)
        self.msg = String()

        asyncio.get_event_loop().create_task(self.read_events())

    async def read_events(self):
        async for event in self.device.async_read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                self.msg.data = f"Key {key_event.keycode} {'pressed' if key_event.keystate == 1 else 'released'}"
                self.publisher_.publish(self.msg)
                self.get_logger().info(f"Publishing: {self.msg.data}")
            elif event.type == evdev.ecodes.EV_ABS:
                abs_event = evdev.categorize(event)
                self.msg.data = f"Key {abs_event.event.code} pressed, value: {abs_event.event.value} "
                self.publisher_.publish(self.msg)
                self.get_logger().info(f"Publishing: {self.msg.data}")

def spin_ros(executor, node):
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.remove_node(node)

def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher()
    
    executor = MultiThreadedExecutor()

    spin_thread = threading.Thread(target=spin_ros, args=(executor, node), daemon=True)
    spin_thread.start()

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()  
        spin_thread.join()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
