import unittest
from unittest.mock import MagicMock, patch
from baidubce.services.bcc import bcc_client, bcc_model
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.bce_client_configuration import BceClientConfiguration
from appbuilder.utils._bcc import InnerBccClient
import uuid
import json

class TestInnerBccClient(unittest.TestCase):

    def setUp(self):
        # 创建配置对象，使用测试的AK/SK
        ak = 'test-access-key-id'
        sk = 'test-secret-access-key'
        self.credentials = BceCredentials(ak, sk)
        self.config = BceClientConfiguration(
            credentials=self.credentials, endpoint='bcc.example.com')
        self.client = InnerBccClient(config=self.config)

        # Mock _send_request 方法，以避免实际的网络请求
        self.client._send_request = MagicMock(return_value='Request Sent')


    def test_create_instance_by_spec_min_params(self):
        # 仅提供必填参数，测试默认值的处理

        spec = 'test-spec'
        image_id = 'test-image-id'

        response = self.client.create_instance_by_spec(
            spec=spec,
            image_id=image_id
        )

        # 验证请求是否发送
        self.assertEqual(response, 'Request Sent')
        self.client._send_request.assert_called_once()

    def test_create_instance_by_spec_no_client_token(self):
        # client_token 为 None，测试自动生成

        spec = 'test-spec'
        image_id = 'test-image-id'
        client_token = None

        with patch('uuid.uuid4', return_value='generated-uuid'):
            response = self.client.create_instance_by_spec(
                spec=spec,
                image_id=image_id,
                client_token=client_token
            )

        # 验证请求是否发送，并检查参数
        self.assertEqual(response, 'Request Sent')
        self.client._send_request.assert_called_once()
        args, kwargs = self.client._send_request.call_args
        self.assertEqual(kwargs['params']['clientToken'], 'generated-uuid')

    def test_create_instance_by_spec_admin_pass(self):
        # 测试 admin_pass 的加密处理

        spec = 'test-spec'
        image_id = 'test-image-id'
        admin_pass = 'test-admin-pass'

        # Mock aes128_encrypt_16char_key 函数
        with patch('appbuilder.utils._bcc.aes128_encrypt_16char_key', return_value='encrypted-pass'):
            response = self.client.create_instance_by_spec(
                spec=spec,
                image_id=image_id,
                admin_pass=admin_pass
            )

            # 验证请求是否发送
            self.assertEqual(response, 'Request Sent')
            self.client._send_request.assert_called_once()
            args, kwargs = self.client._send_request.call_args
            body = json.loads(args[2])
            self.assertEqual(body['adminPass'], 'encrypted-pass')

    def test_create_instance_by_spec_auto_renew(self):
        # 测试 auto_renew_time != 0 且 auto_renew_time_unit 为 None 的情况

        spec = 'test-spec'
        image_id = 'test-image-id'
        auto_renew_time = 1
        auto_renew_time_unit = None

        response = self.client.create_instance_by_spec(
            spec=spec,
            image_id=image_id,
            auto_renew_time=auto_renew_time,
            auto_renew_time_unit=auto_renew_time_unit
        )

        # 验证请求是否发送
        self.assertEqual(response, 'Request Sent')
        self.client._send_request.assert_called_once()
        args, kwargs = self.client._send_request.call_args
        body = json.loads(args[2])
        self.assertEqual(body['autoRenewTime'], auto_renew_time)
        self.assertEqual(body['autoRenewTimeUnit'], 'month')

    def test_create_instance_by_spec_bid_price(self):
        # 测试 bid_price 为 None 的情况

        spec = 'test-spec'
        image_id = 'test-image-id'
        bid_price = None

        response = self.client.create_instance_by_spec(
            spec=spec,
            image_id=image_id,
            bid_price=bid_price
        )

        # 验证请求是否发送
        self.assertEqual(response, 'Request Sent')
        self.client._send_request.assert_called_once()

    def tearDown(self):
        # 重置 _send_request 的调用计数
        self.client._send_request.reset_mock()


if __name__ == '__main__':
    unittest.main()