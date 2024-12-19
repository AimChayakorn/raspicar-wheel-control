import rclpy
from rclpy.node import Node
from rc_pwm_pkg.msg import Pwm
from rc_pwm_pkg.msg import PubPwm

class PublisherSubscriberNode(Node):
    def __init__(self):
        super().__init__('publisher_subscriber_node')

        # Subscriber
        self.subscription = self.create_subscription(
            Pwm,                      
            'topic',               
            self.listener_callback,      
            10                           
        )
        self.subscription

        self.publisher_ = self.create_publisher(
            PubPwm,                      
            'output_pwm',              
            10                           
        )
        self.cur_pwm_left = 0
        self.cur_pwm_right = 0
        self.cur_dif = 0
        self.acc = 0
        self.dcc = 0

        self.timer_period = 0.1  # Publish every 0.5 second
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.get_logger().info('Node initialized: Subscribing to "topic" and publishing to "output_pwm"')

    def listener_callback(self, msg):
        
        if msg.code == 0:
            norm_angle = msg.value / 65525.0 # normalize from 0 to 1
            self.cur_dif = 100 * (norm_angle - 0.5)
        elif msg.code == 2: # accelerate
            self.acc = 255 - msg.value
        elif msg.code == 5: # decelerate
            self.dcc = 255 - msg.value

        #self.get_logger().info(f'Received: "{msg.code}" value: {msg.value}')
        

    def timer_callback(self):
        ret_pwm = PubPwm()
        if self.acc > 0:
            if self.cur_pwm_left + 3 * (self.acc / 255.0) < 100:
                self.cur_pwm_left += 3 * (self.acc / 255.0)
            if self.cur_pwm_right + 3 * (self.acc / 255.0) < 100:
                self.cur_pwm_right += 3 * (self.acc / 255.0)
        elif self.dcc > 0:
            if self.cur_pwm_left - 7 * (self.dcc / 255.0) > 0:
                self.cur_pwm_left -= 7 * (self.dcc / 255.0)
            if self.cur_pwm_right - 7 * (self.dcc / 255.0) > 0:
                self.cur_pwm_right -= 7 * (self.dcc / 255.0)    
        else:
            if self.cur_pwm_left - 5 > 0:
                self.cur_pwm_left -= 5
            else:
                self.cur_pwm_left = 0
            if self.cur_pwm_right - 5 > 0:
                self.cur_pwm_right -= 5
            else:
                self.cur_pwm_right = 0

        ret_pwm.right_pwm = round(self.cur_pwm_right)
        ret_pwm.left_pwm = round(self.cur_pwm_left)
        if self.cur_dif > 0: #turn right
            ret_pwm.right_pwm = round(self.cur_pwm_right - self.cur_dif)
        elif self.cur_dif < 0: #turn left
            ret_pwm.left_pwm = round(self.cur_pwm_left + self.cur_dif)
        
        if ret_pwm.right_pwm < 0:
            ret_pwm.right_pwm = 0
        if ret_pwm.left_pwm < 0:
            ret_pwm.left_pwm = 0
        # Publish the status
        self.publisher_.publish(ret_pwm)
        self.get_logger().info(f'Publishing: Left "{ret_pwm.left_pwm}" , Right "{ret_pwm.right_pwm}"')
        self.get_logger().info(f'Logging: acc "{self.acc}" , dcc "{self.dcc}"')
        self.get_logger().info(f'Logging: right "{self.cur_pwm_right}" , left "{self.cur_pwm_left}"')
        self.get_logger().info(f'Logging: diff "{self.cur_dif}"')

def main(args=None):
    rclpy.init(args=args)
    node = PublisherSubscriberNode()

    try:
        rclpy.spin(node)  # Keep the node alive
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
