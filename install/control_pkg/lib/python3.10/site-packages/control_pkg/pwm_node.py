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
        self.acc = 255
        self.dcc = 255
        self.is_listening = False # listening state

        self.timer_period = 0.1  # Publish every 0.5 second
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.get_logger().info('Node initialized: Subscribing to "topic" and publishing to "output_pwm"')

    def listener_callback(self, msg):
        self.is_listening = True
        
        if msg.code == 0:
            norm_angle = msg.value / 65525.0 # normalize from 0 to 1
            if norm_angle > 0.5 and self.cur_pwm_right > 0:
                self.cur_dif = 20 * (norm_angle - 0.5)
            elif self.cur_pwm_left > 0:
                self.cur_dif = 20 * (norm_angle - 0.5)
        elif msg.code == 2: # accelerate
            self.acc = msg.value
            norm_acc = msg.value / 255.0 # normalize from 0 to 1
            if self.cur_pwm_left < 100:
                self.cur_pwm_left += 0.1 * (1 - norm_acc)
            if self.cur_pwm_right < 100:
                self.cur_pwm_right += 0.1 * (1 - norm_acc)
        elif msg.code == 5: # decelerate
            self.dcc = msg.value
            norm_dcc = msg.value / 255.0 # normalize from 0 to 1
            if self.cur_pwm_left > 0:
                self.cur_pwm_left -= 0.1 * (1 - norm_dcc)
            if self.cur_pwm_right > 0:
                self.cur_pwm_right -= 0.1 * (1 - norm_dcc)
        #self.get_logger().info(f'Received: "{msg.code}" value: {msg.value}')
        

    def timer_callback(self):
        ret_pwm = PubPwm()
        if not (self.is_listening or self.acc != 255 or self.dcc != 255): # slow down if pedal is released
            if self.cur_pwm_right > 0:
                self.cur_pwm_right -= 1
            if self.cur_pwm_left > 0:
                self.cur_pwm_left -= 1

        if self.acc != 255 and not self.is_listening: # continue accelerate if pedal is pressed
            hold_acc = self.acc / 255.0 # normalize from 0 to 1
            if self.cur_pwm_left < 100:
                self.cur_pwm_left += 3 * (1 - hold_acc)
            if self.cur_pwm_right < 100:
                self.cur_pwm_right += 3 * (1 - hold_acc)

        if self.dcc != 255 and not self.is_listening: # continue decelerate if pedal is pressed
            hold_dcc = self.dcc / 255.0 # normalize from 0 to 1
            if self.cur_pwm_left > 0:
                self.cur_pwm_left -= 10 * (1 - hold_dcc)
            if self.cur_pwm_right > 0:
                self.cur_pwm_right -= 10 * (1 - hold_dcc)

        if self.cur_pwm_left - self.cur_dif < 0 :
            self.cur_pwm_left = 0
        elif self.cur_pwm_left - self.cur_dif > 100 :
            self.cur_pwm_left -= self.cur_pwm_left + self.cur_dif - 100
        if self.cur_pwm_right + self.cur_dif < 0 :
            self.cur_pwm_right = 0
        elif self.cur_pwm_right + self.cur_dif > 100 :
            self.cur_pwm_right -= self.cur_pwm_right + self.cur_dif - 100
        ret_pwm.left_pwm = round(self.cur_pwm_left - self.cur_dif)
        ret_pwm.right_pwm = round(self.cur_pwm_right + self.cur_dif)

        self.is_listening = False        
        # Publish the status
        self.publisher_.publish(ret_pwm)
        self.get_logger().info(f'Publishing: Left "{ret_pwm.left_pwm}" , Right "{ret_pwm.right_pwm}"')

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
